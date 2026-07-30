FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app:/app/src/generated

COPY pyproject.toml ./
RUN python3 -c 'import re,tomllib;deps=tomllib.load(open("pyproject.toml","rb")).get("project",{}).get("dependencies",[]);open("requirements.txt","w").write("\n".join(re.sub(r"\s*\(([^)]+)\)",r"\1",d)for d in deps))' \
	&& pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY main.py ./

CMD ["sh", "-c", "python main.py"]