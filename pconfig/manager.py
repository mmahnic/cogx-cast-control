#!/usr/bin/python
# vim:set fileencoding=utf-8 sw=4 ts=8 et:vim #
# Author: Marko Mahnič
# Created: March 2011

from properties import CPropertySet
import re

regSimple = re.compile (r"\$([a-z_0-9]+)", re.IGNORECASE)
regSimpleBrace = re.compile (r"\${([a-z_0-9]+)}", re.IGNORECASE)

def _xe(shexpr, env):
    for rx in [regSimple, regSimpleBrace]:
        mos = [mo for mo in rx.finditer(shexpr)]
        mos.reverse()
        for m in mos:
            if env.has_key(m.group(1)): v = env[m.group(1)]
            else: v = ""
            shexpr = shexpr.replace(m.group(0), v)

    return shexpr

class CServerInfo(CPropertySet):
    def __init__(self, name, **kwargs):
        super(CServerInfo, self).__init__(name, **kwargs)
        self.enabled = False
        self._command = None
        self._customCommandVar = None
        self.isServer = True
        self.workdir = None
        self.defaultVars = []
        self.termWithSigInt = False
        self._paramPreprocess = None

        if 'group' in kwargs: self.group = kwargs['group']
        else: self.group = 'A'

        if 'server' in kwargs:
            self.isServer = True if kwargs['server'] else False

    def setParamProcessor(self, processor):
        self._paramPreprocess = processor

    def setVar(self, name, value):
        parts = value.split("\n")
        parts = [ p.strip() for p in parts if p.strip() != ""]
        value = " ".join(parts)
        self.defaultVars.append( (name, value) )

    def _valid_lines(self, strValue):
        lines = [l.strip() for l in strValue.split("\n") if l.strip() != ""]
        lines = [l for l in lines if not l.startswith("#")]
        return lines

    def setPathList(self, name, value):
        #self.setVar(name, ":".join(self._valid_lines(value)))
        pl = "<pathlist>\n%s\n</pathlist>" % ("\n".join(self._valid_lines(value)))
        self.defaultVars.append((name, pl))

    def setCommand(self, cmd, workdir=None):
        self._command = " ".join(self._valid_lines(cmd))
        self.workdir = workdir

    def setCustomCommandVar(self, varname):
        self._customCommandVar = varname

    def getCommand(self, environ=None):
        cmd = ""
        if environ != None and self._customCommandVar != None and self._customCommandVar in environ:
            cmd = _xe(environ[self._customCommandVar], environ)
            cmd = cmd.strip()
        if cmd == "":
            cmd = self._command
        if self._paramPreprocess != None:
            cmdname = cmd.split()[0]
            if cmdname.startswith("[") and cmdname.endswith("]"):
                cmdlen = len(cmdname)
                cmdname = cmdname.strip(" []")
                default = "echo"
                #parts = cmdname.split(":")
                #cmdname = parts[0]
                #if len(parts) > 1: default = ":".join(parts[1:])
                newcmdname = self._paramPreprocess(cmdname, default, self)
                cmd = "%s %s" % (newcmdname, cmd[cmdlen:])
        return cmd

    def getParameters(self):
        params = {}
        if self._paramPreprocess != None:
            for p in self.properties:
                params[p.name] = "%s" % self._paramPreprocess("%s" % p.name, "%s" % p.value, self)
        else:
            for p in self.properties:
                params[p.name] = "%s" % p.value
        return params if len(params) > 0 else None

    def getEnvVarScript(self):
        if len(self.defaultVars) < 1: return None
        script = "\n".join(["%s=%s" % (v[0], v[1]) for v in self.defaultVars])
        return script

class CServerManager:
    def __init__(self):
        self.servers = []

    def addServersFromFile(self, filename):
        srvrs = self.discoverServers(filename)
        self.servers = self.servers + srvrs
        return srvrs

    def getServerInfo(self, name):
        for c in self.servers:
            if c.name == name:
                return c
        return None

    # Load config files to discover servers
    def discoverServers(self, filename):
        srvrs = []

        def Server(name, **kwargs):
            csi = CServerInfo(name, **kwargs)
            srvrs.append(csi)
            return csi

        glvars = { 'Server': Server }
        try:
            exec open(filename).read() in glvars
        except Exception as e:
            print e

        return srvrs

    def saveServerConfig(self, configParser, rootdir=None):
        pathprefix = ""
        if rootdir != None:
            pathprefix = rootdir + '/'

        p = configParser
        for csi in self.servers:
            section = "Server:%s" % (csi.name.upper())
            if not p.has_section(section):
                p.add_section(section)
            p.set(section, "enabled", "1" if csi.enabled else "0")
            for prop in csi.properties:
                v = prop.value
                if v == None: v = ""
                try:
                    if len(pathprefix) > 2 and v.startswith(pathprefix):
                        v = v[len(pathprefix):]
                except: pass
                p.set(section, prop.name, "%s" % v)

            for prop in csi.properties:
                if not prop.mruEnabled: continue

                section = "MRU:%s-%s" % (csi.name.upper(), prop.name)
                p.remove_section(section)
                p.add_section(section)

                if not prop.mruHistory: continue
                if len(prop.mruHistory) < 1: continue

                for i,h in enumerate(prop.mruHistory):
                    try:
                        if len(pathprefix) > 2 and h.startswith(pathprefix):
                            h = h[len(pathprefix):]
                    except: pass
                    p.set(section, "%03d" % (i+1), "%s" % h)

    def loadServerConfig(self, configParser):
        #import ConfigParser
        #p = ConfigParser.RawConfigParser()
        #p.read(filename)
        p = configParser
        for csi in self.servers:
            section = "Server:%s" % csi.name.upper()
            if not p.has_section(section): continue
            option = "enabled"
            if p.has_option(section, option):
                csi.enabled = p.getint(section, option)
            for prop in csi.properties:
                option = "%s" % prop.name
                if not p.has_option(section, option): continue
                prop.value = p.get(section, option)
                prop.mruHistory = None

            for prop in csi.properties:
                if not prop.mruEnabled: continue
                section = "MRU:%s-%s" % (csi.name.upper(), prop.name)
                if not p.has_section(section): continue
                items = sorted(p.items(section))
                prop.mruHistory = [ v[1] for v in items ]


