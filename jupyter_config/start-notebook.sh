#!/bin/bash
# ==============================
# Custom startup script for Jupyter
# Compatible with Jupyter Server 2.x / JupyterLab 4.x
# ==============================

# Generar hash con la librería nueva
HASH=$(python3 -c "from jupyter_server.auth import passwd; print(passwd('$JUPYTER_PASSWORD'))")

# Crear configuración de Jupyter
mkdir -p ~/.jupyter
cat > ~/.jupyter/jupyter_notebook_config.py <<EOF
c = get_config()
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.password = u'$HASH'
# No desactivamos autenticación (solo quitamos token)
c.ServerApp.token = ''
EOF

# Ejecutar Jupyter normalmente
exec start-notebook.sh
