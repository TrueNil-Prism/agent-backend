# agent-backend

Steps to start the server
1. ssh -i ~/Downloads/dev-truenil-keypair.pem admin@10.0.150.153
2. cd /home/admin/agent-backend
3. source ./venv/bin/activate
4. cd src 
5. nohup uvicorn truenil.api.main:app --host 0.0.0.0 --port 9000 --reload &