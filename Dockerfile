#Use an official Python image as the base image
FROM python:3.8-slim-buster 

#set the working directory in the container to /app
WORKDIR /app 

#copy the contents of the current directory into the container /app directory
COPY . /app

#upgrade pip
RUN pip install --upgrade pip

#install any needed packages
RUN pip install --no-cache-dir -r requirements.txt 

#set the default comands to run when starting the container
CMD ["python", "app.py"]