FROM davidbliu/etcd_base

#
# install sshd
#
RUN apt-get install -y sudo ntp openssh-server supervisor
RUN mkdir -p /var/run/sshd
RUN adduser --gecos "" container
RUN echo 'container:container' | sudo -S chpasswd
RUN echo 'container ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN sed -i -e 's/^\(session\s\+required\s\+pam_loginuid.so$\)/#\1/' /etc/pam.d/sshd

# Install Python Setuptools
RUN apt-get install -y python-setuptools
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential
RUN apt-get install -y python python-dev python-distribute python-pip

# Install pip
RUN pip install flask
RUN pip install marathon
RUN pip install flask-bootstrap

ADD . /opt/theseus
WORKDIR /opt/theseus

EXPOSE 22 5000

CMD python -u viewer.py