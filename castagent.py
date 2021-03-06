#!/usr/bin/env python
# vim:set fileencoding=utf-8 sw=4 ts=8 et:vim
# Author:  Marko Mahnič
# Created: jan 2010 

import os, sys, time, re
import shutil
import optparse
from string import Template

from core import castagentsrv, procman, options, messages, logger, log4util
from core.castagentsrv import RSYNC_DAEMON
LOGGER = logger.get()

import pconfig
from pconfig.configwidget import CConfigWidget
from pconfig.manager import CServerManager

import threading
import Ice
import core.modice
import icemodule.castcontrol.CastAgent as CastAgent

CODEF = '\x1b[0m'
BGK = '\x1b[1;40m'
BGY = '\x1b[1;43m'
FGR = '\x1b[1;31m'
FGB = '\x1b[1;34m'
FGW = '\x1b[1;37m'


class CLogDisplayer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name="CLogDisplayer")
        self.log = messages.CLogMerger()
        self.logSink = messages.CLogMessageSink()
        self.log.addSink(self.logSink)
        self.showFlush = True # option
        self.showWarning = True # option
        self.showError = True # option
        self.reError = re.compile(r"\b(error)\b", re.IGNORECASE)
        self.reWarning = re.compile(r"\b(warning)\b", re.IGNORECASE)
        self._isRunning = False
        self.out = sys.stdout
        # self.out = open("out.tmp", "w")

    def _markWords(self, text, coDefault=CODEF):
        text = self.reError.sub(FGW + BGY + r'\1' + coDefault, text)
        text = self.reWarning.sub(FGW + BGY + r'\1' + coDefault, text)
        return text

    def pullLogs(self):
        mods = False
        self.log.merge()
        if self.logSink.hasMessages():
            msgs = self.logSink.getNewMessages(100)
            for m in msgs:
                text = m.getText().rstrip()
                co = None
                if m.msgtype != messages.CMessage.CASTLOG:
                    if m.msgtype == messages.CMessage.WARNING:
                        if not self.showWarning: continue
                        text = self._markWords(text, CODEF+FGB)
                        co = FGB
                    elif m.msgtype == messages.CMessage.ERROR:
                        if not self.showError: continue
                        text = self._markWords(text, CODEF+FGR)
                        co = FGR
                    elif m.msgtype == messages.CMessage.FLUSHMSG:
                        if not self.showFlush: continue
                        text = self._markWords(text, CODEF+FGW)
                        co = FGW
                if co != None: self.out.write(co)
                self.out.write(text.encode("ascii", "replace"))
                self.out.write(CODEF)
                self.out.write("\n")
            mods = True
        return mods

    def run(self):
        self._isRunning = True
        while self._isRunning:
            self.pullLogs()
            time.sleep(0.3)
        self.pullLogs()

    def shutdown(self):
        self._isRunning = False


class CConsoleAgent:
    def __init__(self, appOptions):
        port = appOptions.port
        self.manager = procman.CProcessManager("localhost")
        self._options = options.CCastOptions()
        self._options.loadConfig(appOptions.config)
        self._options.configEnvironment()
        self.address = "tcp -p %d" % port
        self.agent = None
        self.mainLog = None

        self.serverManager = CServerManager()
        fn = os.path.join(os.path.dirname(pconfig.__file__), "castservers.txt")
        self.serverManager.addServersFromFile(fn)
        fn = os.path.join(os.path.dirname(pconfig.__file__), "cogxservers.txt")
        self.serverManager.addServersFromFile(fn)

        self._options.appOptions = appOptions
        self._initLocalProcesses(appOptions)

    def __del__(self):
        self.manager.stopReaderThread()

    def _addProcess(self, name, dictParams=None):
        csi = self.serverManager.getServerInfo(name)
        if csi == None:
            LOGGER.error("Server '%s' is not registered." % name)
            return
        if dictParams != None:
            for (k,v) in dictParams.iteritems():
                p = csi.getProperty(k)
                if p == None:
                    LOGGER.error("Server '%s' has no property named '%s'." % (name, k))
                    continue
                p.value = v
        extenv = self._options.getExtendedEnviron(defaults=csi.getEnvVarScript())
        command = self._options.xe(csi.getCommand(extenv), environ=extenv)
        workdir = self._options.xe(csi.workdir, environ=extenv) if csi.workdir != None else None
        #print command
        #print csi.getParameters()
        proc = procman.CProcess(name=name, command=command, params=csi.getParameters(),
                workdir=workdir, allowTerminate=not csi.isServer)
        self.manager.addProcess(proc)

    def _initLocalProcesses(self, appOptions):
        self._addProcess('cast-java')
        self._addProcess('cast-cpp')
        self._addProcess('cast-python')

        p = procman.CProcess(procman.LOG4J_PROCESS, self._options.xe("${CMD_LOG4J_SERVER}"))
        p.messageProcessor = log4util.CLog4MessageProcessor()
        self.manager.addProcess(p)

        if appOptions.player_cfg != None:
            # TODO: Player configuration (file contents) could also be sent from the remote machine
            if not os.path.exists(appOptions.player_cfg):
                LOGGER.warn("Player configuration file '%s' not found." % appOptions.player_cfg)
            else:
                self._addProcess('Player', { 'CONFIG': appOptions.player_cfg })

        if appOptions.golem_cfg != None:
            self._addProcess('Golem') # NOTE: No configuration is needed any more.

        if appOptions.gazebo_world != None:
            if not os.path.exists(appOptions.gazebo_world):
                LOGGER.warn("Gazebo world file '%s' not found." % appOptions.gazebo_world)
            else:
                self._addProcess('Gazebo', { 'WORLD': appOptions.gazebo_world })

        if appOptions.abducer != None and appOptions.abducer:
            self._addProcess('Abducer')

        if appOptions.display_srv != None and appOptions.display_srv:
            self._addProcess('Display')

        if appOptions.peekabot != None and appOptions.peekabot:
            self._addProcess('Peekabot')

        if appOptions.text2speech != None and appOptions.text2speech:
            self._addProcess('Mary.tts')

        if appOptions.can_build:
            cmd = "make [TARGET]"
            proc = procman.CProcess("BUILD", cmd)
            proc.allowTerminate = True
            self.manager.addProcess(proc)

        if  appOptions.can_rsync:
            RSYNC_DAEMON.port = appOptions.rsync_port
            cmd = RSYNC_DAEMON.getDaemonCommand()
            p = procman.CProcess("RSYNC", cmd)
            self.manager.addProcess(p)

        if  appOptions.cleanup_script != None:
            self._addProcess('Cleanup', { 'SCRIPT': appOptions.cleanup_script })

    def _initMessagePump(self):
        self.mainLog = CLogDisplayer()
        for proc in self.manager.proclist:
            self.mainLog.log.addSource(proc)
        # XXX LOGGER not added if it's a CStdoutLogger - it will print it's own messages
        self.mainLog.log.addSource(LOGGER)
        self.mainLog.start()


    def _shutdown(self, agent):
        count = 10
        agent.shutdown()
        LOGGER.log("Shutdown")
        time.sleep(0.5)
        while agent.isAlive():
            count -= 1
            LOGGER.log("... waiting for shutdown (%d)" % count)
            if count <= 0: break
            time.sleep(1.0)
        if agent.isAlive():
            LOGGER.warn("ICE Server didn't shut down")
        else:
            LOGGER.log("ICE Server stopped.")

    def startLogging(self):
        self._initMessagePump()

    def startServing(self):
        if self.agent != None: self.stopServing()
        self.agent = castagentsrv.CCastSlave(self.manager, self._options, self.address)
        self.agent.start()
        time.sleep(0.2)

    def stopServing(self):
        if self.agent != None: self._shutdown(self.agent)
        self.agent = None
        self.manager.stopReaderThread()
        if self.mainLog != None:
            self.mainLog.shutdown()

def createOptionParser():
    usage = "Usage: %prog [options] args"
    parser = optparse.OptionParser(usage)

    #parser.add_option("-v", "--verbose", action="store", type="int", dest="verbose")
    #parser.add_option("-q", "--quiet", action="store_const", const=0, dest="verbose")
    parser.add_option("-p", "--port", action="store", type="int", default=castagentsrv.SLAVE_PORT, dest="port",
            help="Set the port number on which this agent will be listening. Default=%d." % castagentsrv.SLAVE_PORT)

    parser.add_option("-c", "--config", action="store", type="string", default="castcontrol.conf", dest="config",
            help="Set a configuration file. Default=castcontrol.conf.")

    parser.add_option("", "--build", action="store_true", dest="can_build", default=False,
            help="Build the project when required by the remote process.")

    parser.add_option("", "--rsync", action="store_true", dest="can_rsync", default=False,
            help="Allow the agent to receive code from the remote process via rsync into current directory.")

    parser.add_option("", "--rsync-port", action="store", type="int", dest="rsync_port",
            default=RSYNC_DAEMON.port,
            help="The rsync daemon will serve on this port (default=%d)." % RSYNC_DAEMON.port)

    parser.add_option("", "--player", action="store", type="string", default=None, dest="player_cfg",
            help=
            "Set the Player configuration file. If not set, Player won't be started by this agent. "
            "Env: CMD_PLAYER"
           )

    parser.add_option("", "--golem", action="store", type="string", default=None, dest="golem_cfg",
            help=
            "Set the Golem configuration file. If not set, Golem won't be started by this agent. "
            "Env: CMD_GOLEM, CMD_GOLEM_WORKDIR"
           )

    parser.add_option("", "--gazebo-world", action="store", type="string", default=None, dest="gazebo_world",
            help=
            "Set the Gazebo world file. If not set, Gazebo won't be started by this agent. "
            "Env: CMD_GAZEBO"
           )

    parser.add_option("", "--peekabot", action="store_true", dest="peekabot", default=False,
            help=
            "If set, Peekabot will be started by this agent. "
            "Env: CMD_PEEKABOT"
           )

    parser.add_option("", "--abducer", action="store_true", dest="abducer", default=False,
            help=
            "If set, Abducer will be started by this agent. "
            "Env: CMD_ABDUCER"
           )

    parser.add_option("", "--text2speech", action="store_true", dest="text2speech", default=False,
            help=
            "If set, Text To Speech server (Mary) will be started by this agent. "
            "Env: CMD_SPEECH_SERVER"
           )

    parser.add_option("", "--display-server", action="store_true", dest="display_srv", default=False,
            help=
            "If set, Display Server will be started by this agent. "
            "Env: CMD_DISPLAY_SERVER"
           )

    parser.add_option("", "--cleanup-script", action="store", type="string", default=None, dest="cleanup_script",
            help=
            "Set the cleanup script. The script will be executed before the CAST servers are started."
           )

    return parser


def parseOptions(parser):
    (options, args) = parser.parse_args()
    # if options.verbose > 3: print "Options parsed"
    # if len(args) != 1: parser.error("incorrect number of arguments")
    return (options, args)


def main():
    parser = createOptionParser()
    opts, args = parseOptions(parser)
    print "Settings:"
    for o in dir(opts):
        if o.startswith("_"): continue
        if o in ['read_file', 'read_module', 'ensure_value']: continue
        try: print "%14s:\t%s" % (o, eval("opts.%s" % o))
        except: pass
    agent = CConsoleAgent(opts)
    agent.startLogging()
    agent.startServing()
    try:
        print "Press Ctrl-C to stop serving."
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        print "\nKeyboard Interrupt\n"
    except:
        print "\nInterrupted\n"
    agent.stopServing()

if __name__ == "__main__": main()

