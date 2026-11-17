FROM python:3.13-slim

# don't generate python files
ENV PYTHONDONTWRITEBYTECODE=1

# python prints won't use buffer
ENV PYTHONUNBUFFERED=1

# work dir, al copied files will be placed here
WORKDIR /app

COPY rpc_assignment/common/ ./common/
COPY rpc_assignment/server/ ./server/

# notices user to use port 5000
EXPOSE 5000

# execute server
CMD ["python3", "-m", "server.server"]
