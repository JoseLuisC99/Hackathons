
FROM python:3.11-alpine
WORKDIR /app

# Install Java (for OpenAPI generation)
RUN apk update \
&& apk upgrade \
&& apk add --no-cache bash \
&& apk add --no-cache --virtual=build-dependencies unzip \
&& apk add --no-cache curl \
&& apk add --no-cache openjdk17-jre

# Create a non-root user
RUN adduser --disabled-password --gecos "" myuser

# Change ownership of /app to myuser
RUN chown -R myuser:myuser /app

# Switch to the non-root user
USER myuser

# Set up environment variables - Start
ENV PATH="/home/myuser/.local/bin:$PATH"

ENV GOOGLE_GENAI_USE_VERTEXAI=1
ENV GOOGLE_CLOUD_PROJECT=hackathons-projects
ENV GOOGLE_CLOUD_LOCATION=us-central1

# Set up environment variables - End

# Install ADK - Start
RUN pip install google-adk==1.3.0
# Install ADK - End

# Copy agent - Start

COPY "agents/api_builders/" "/app/agents/api_builders/"
RUN pip install -r "/app/agents/api_builders/requirements.txt"

# Copy agent - End

EXPOSE 8000

CMD adk web --port=8000 --host=0.0.0.0    --trace_to_cloud "/app/agents"
