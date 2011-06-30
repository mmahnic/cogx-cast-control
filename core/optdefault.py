# This file is auto-generated. Do not edit
environment="""
# Environment variables
COGX_ROOT=[PWD]

CAST_DIR=/usr/local
CAST_INSTALL_ROOT=${CAST_DIR}

CUDA_ROOT=/usr/local/cuda
CURE_LIB_DIR=/usr/local/lib/cure
MERCURY_ROOT=/usr/local/lib/mercury
#MATLAB_ARCH=glnx86
MATLAB_ARCH=glnxa64
MATLAB_RUNTIME_DIR=/opt/MATLAB/MATLAB_Compiler_Runtime/v78/runtime/${MATLAB_ARCH}
# MATLAB_RUNTIME_DIR=/usr/share/matlabR2008a/bin/${MATLAB_ARCH}

COGX_BUILD_DIR=${COGX_ROOT}/BUILD
COGX_LIB_DIR=${COGX_ROOT}/output/lib
COGX_CLASS_DIR=${COGX_ROOT}/output/classes

CAST_BIN_PREFIX=bin
CAST_BIN_DIR=${CAST_INSTALL_ROOT}/${CAST_BIN_PREFIX}

CAST_LIB_PREFIX=lib/cast
CAST_LIB_DIR=${CAST_INSTALL_ROOT}/${CAST_LIB_PREFIX}

CAST_CONFIG_PATH=share/cast/config/cast_ice_config
CAST_ICE_CONFIG=${CAST_INSTALL_ROOT}/${CAST_CONFIG_PATH}

ICE_CONFIG=${CAST_ICE_CONFIG}

PATH=<pathlist>
   ${COGX_ROOT}/output/bin
   ${CUDA_ROOT}/bin
   ${MERCURY_ROOT}/bin
   ${PATH}
</pathlist>

LD_LIBRARY_PATH=<pathlist>
   ${LD_LIBRARY_PATH}
   ${CAST_LIB_DIR}
   ${COGX_LIB_DIR}
   ${CURE_LIB_DIR}
   ${CUDA_ROOT}/lib
   ${MATLAB_RUNTIME_DIR}
</pathlist>
DYLD_LIBRARY_PATH=${DYLD_LIBRARY_PATH}:${LD_LIBRARY_PATH}

PYTHONPATH=<pathlist>
   ${CAST_LIB_DIR}/python
   ${COGX_ROOT}/output/planner
   ${COGX_ROOT}/output/python
   ${PYTHONPATH}
</pathlist>

CLASSPATH=<pathlist>
   ${CLASSPATH}
   ${CAST_INSTALL_ROOT}/share/java/cast.jar
   ${COGX_CLASS_DIR}
   <glob>${COGX_CLASS_DIR}/coma.libs/*.jar</glob> # glob expressions must be on one line
   /usr/share/java/Ice.jar
   /usr/share/java/ant-ice.jar
   /usr/share/java/log4j-1.2.jar
   /usr/share/java/xstream-1.3.1.jar
</pathlist>

# To redirect the v11n output to a standalone DisplayServer add the
# parameter --redirect-to-host "hostnale" to a DisplayServer component
# in a cast file.
# OBSOLETE: V11N can run standalone when --standalone-display-host is set
# OBSOLETE: All clients that use the display server should include the 
# OBSOLETE: parmeters: $V11N_STANDALONE $V11N_STANDALONE_HOST 
V11N_STANDALONE=--standalone-display-host
V11N_STANDALONE_HOST=localhost

CMD_JAVA=java -ea -classpath ${CLASSPATH}

CMD_CPP_SERVER=${CAST_BIN_DIR}/cast-server-c++
CMD_CPP_SERVER_DEBUG=ddd --eval-command=run ${CAST_BIN_DIR}/cast-server-c++ 

CMD_PYTHON_SERVER=python -m ComponentServer

CMD_JAVA_SERVER=${CMD_JAVA} cast.server.ComponentServer
CMD_JAVA_SERVER_DEBUG=ddd -jdb -launch cast.server.ComponentServer

CMD_CAST_CLIENT=${CMD_JAVA} cast.clients.CASTClient -f [CAST_CONFIG]
CMD_PLAYER=player [PLAYER_CONFIG]
CMD_GOLEM=golemTinyIce [GOLEM_CONFIG]
CMD_PEEKABOT=peekabot
CMD_LOG4J_SERVER=<multiline>
   java -ea -classpath ${CLASSPATH}
   org.apache.log4j.net.SimpleSocketServer [LOG4J_PORT] [LOG4J_SERVER_CONFIG]
</multiline>
CMD_DISPLAY_SERVER=${COGX_ROOT}/output/bin/display-server

# Abducer Server
ABDUCER_ROOT=${COGX_ROOT}/subarchitectures/dialogue.sa/external/abducer-current
CMD_ABDUCER_SERVER=<multiline>
   ${ABDUCER_ROOT}/abducer-server-bin
   -n "AbducerServer"
   -e "default -p 10000"
   -a ${ABDUCER_ROOT}/abduction-engine
</multiline>

MARY_ROOT=${COGX_ROOT}/tools/mary
MARY_CLASSPATH=<pathlist>
   ${MARY_ROOT}/java/mary-common.jar
   ${MARY_ROOT}/java/log4j-1.2.15.jar
</pathlist>
CMD_SPEECH_SERVER=<multiline>
   java -ea -Xms40m -Xmx1g -classpath ${MARY_CLASSPATH}
   -Dmary.base=${MARY_ROOT} 
   marytts.server.Mary
</multiline>

"""
cleanup="""
#dc1394_reset_bus
#rm robotpose.ccf
#tools/scripts/peekabotdata ${COGX_ROOT}/instantiations/peekabot-models/data

"""
useroptions="""

# Configure an external editor. If the external editor doesn't work
# the program will use the internal editor
EDITOR=internal
#EDITOR=gvim --servername GVIM --remote-silent %l[+:] %s
#EDITOR=xemacs %l[+] %s
#EDITOR=kate %l[-l ] %s
#EDITOR=gedit %l[+] %s
#EDITOR=xjed %s %l[-g ]
#EDITOR=edit %l[+] %s
#EDITOR=open -a textwrangler %s

# Configure the terminal to be used with the "Start Terminal" command.
#TERMINAL=konsole --workdir '%s'
#TERMINAL=konsole --new-tab --workdir '%s'
#TERMINAL=gnome-terminal --working-directory='%s'

# Set the limits for the number of log messages displayed (100-10000)
#MAINLOGLINES=500
#BUILDLOGLINES=500
"""
log4joptions="""

# Startup configuration for org.apache.log4j.net.SimpleSocketServer 
# rootLogger entries are the following: level, consoleAppender-id, xmlFileAppender-id
[LOG4J.SimpleSocketServer.conf]
log4j.rootLogger=TRACE, srvConsole, srvXmlFile

[LOG4J.SimpleSocketServer.console]
log4j.appender.srvConsole=org.apache.log4j.ConsoleAppender
log4j.appender.srvConsole.Threshold=${LEVEL}
log4j.appender.srvConsole.layout=org.apache.log4j.PatternLayout
log4j.appender.srvConsole.layout.ConversionPattern=[%p %c: %m]%n
# log4j.appender.srvConsole.layout.ConversionPattern=%30c [ %05p ] - %m %n

[LOG4J.SimpleSocketServer.xmlfile]
log4j.appender.srvXmlFile=org.apache.log4j.FileAppender
log4j.appender.srvXmlFile.Threshold=${LEVEL}
log4j.appender.srvXmlFile.File=${LOGFILE}
log4j.appender.srvXmlFile.Append=true
log4j.appender.srvXmlFile.layout=org.apache.log4j.xml.XMLLayout

[LOG4J.SimpleSocketServer.XMLLayout.head]
<?xml version="1.0" encoding="UTF-8"?>
<log4j:logsequence xmlns:log4j="http://jakarta.apache.org/log4j/" user="${USER}" time="${NOW}">

# Startup configuration for clients other than the SimpleSocketServer
# rootLogger entries are the following: level, consoleAppender-id, socketAppender-id
[LOG4J.client.conf]
log4j.rootLogger=TRACE, cliConsole, cliSocketApp

[LOG4J.client.console]
log4j.appender.cliConsole=org.apache.log4j.ConsoleAppender
log4j.appender.cliConsole.Threshold=${LEVEL}
log4j.appender.cliConsole.layout=cast.core.logging.ComponentLayout
log4j.appender.cliConsole.layout.ConversionPattern=%S[%P %i: %m]%n%E
#log4j.appender.cliConsole.layout.ConversionPattern=%S %30c [ %05p ] - %m %n%E

[LOG4J.client.socket]
log4j.appender.cliSocketApp=org.apache.log4j.net.SocketAppender
# TODO: $LEVEL could be MAX of all levels in SimpleSocketServer
# log4j.appender.SocketApp.Threshold=${LEVEL}
log4j.appender.cliSocketApp.Port=${PORT}
log4j.appender.cliSocketApp.RemoteHost=${HOST}

"""
