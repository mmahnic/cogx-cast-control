# This file is auto-generated. Do not edit
environment="""
COGX_ROOT=[PWD]
COGX_BUILD_DIR=${COGX_ROOT}/BUILD
COGX_LIB_DIR=${COGX_ROOT}/output/lib
COGX_PY_DIR=${COGX_ROOT}/output/python
COGX_CLASS_DIR=${COGX_ROOT}/output/classes

CAST_DIR=/usr/local
CAST_INSTALL_ROOT=${CAST_DIR}

CAST_BIN_PREFIX=bin
CAST_BIN_DIR=${CAST_INSTALL_ROOT}/${CAST_BIN_PREFIX}

CAST_LIB_PREFIX=lib/cast
CAST_LIB_DIR=${CAST_INSTALL_ROOT}/${CAST_LIB_PREFIX}
CAST_PY_DIR=${CAST_LIB_DIR}/python

CAST_JAR=${CAST_INSTALL_ROOT}/share/java/cast.jar

CAST_CONFIG_PATH=share/cast/config/cast_ice_config
CAST_ICE_CONFIG=${CAST_INSTALL_ROOT}/${CAST_CONFIG_PATH}

ICE_CONFIG=${CAST_ICE_CONFIG}
ICE_JARS=/usr/share/java/Ice.jar:/usr/share/java/ant-ice.jar

PATH=${COGX_ROOT}/output/bin:${PATH}
LD_LIBRARY_PATH=${CAST_LIB_DIR}:${COGX_LIB_DIR}:/usr/local/cuda/lib:${LD_LIBRARY_PATH}
DYLD_LIBRARY_PATH=${CAST_LIB_DIR}:${COGX_LIB_DIR}:/usr/local/cuda/lib:${DYLD_LIBRARY_PATH}

CLASSPATH=${CLASSPATH}:${ICE_JARS}:${CAST_JAR}:${COGX_CLASS_DIR}
CMD_JAVA=java -ea -classpath ${CLASSPATH}

PYTHONPATH=${PYTHONPATH}:${CAST_PY_DIR}:${COGX_PY_DIR}

CMD_CPP_SERVER=${CAST_BIN_DIR}/cast-server-c++
CMD_JAVA_SERVER=${CMD_JAVA} cast.server.ComponentServer
CMD_PYTHON_SERVER=python -m ComponentServer
CMD_CAST_CLIENT=${CMD_JAVA} cast.clients.CASTClient -f [CAST_CONFIG]
CMD_PLAYER=player [PLAYER_CONFIG]
CMD_PEEKABOT=peekabot
"""
cleanup="""
#dc1394_reset_bus
"""
useroptions="""
#EDITOR=emacs %s
#EDITOR=kate %s
#EDITOR=gedit %s
#EDITOR=gvim --servername CAST --remote %s
"""