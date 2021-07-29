FROM alpine:edge

COPY rootfs /

#Install software for vpn and proxy
RUN apk --update add --no-cache --upgrade \
  curl \
  openvpn \
  py3-setuptools \
  supervisor \
  openssh \
  busybox-extras \
  nmap \
  unbound \
  openresolv \
  squid 
  


RUN apk --update --allow-untrusted --repository http://dl-4.alpinelinux.org/alpine/edge/testing/ add       bash       openconnect && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

RUN mkdir /var/run/sshd
RUN mkdir /log
RUN mkdir /shared
RUN touch /log/supervisord.log

RUN echo "root:root" | chpasswd
RUN sed -i s/#PermitRootLogin.*/PermitRootLogin\ yes/ /etc/ssh/sshd_config
RUN sed -i s/AllowTcpForwarding.*/AllowTcpForwarding\ yes/ /etc/ssh/sshd_config

COPY conf/supervisord.conf /etc/supervisord.conf
COPY authorized_keys /root/.ssh/authorized_keys
COPY conf/squid*.conf /etc/squid/
COPY conf/resolvconf.conf /etc
COPY conf/unbound.conf /etc/unbound/unbound.conf

RUN chmod 600 /root/.ssh/authorized_keys

EXPOSE 22
EXPOSE 3128
EXPOSE 53/udp

VOLUME ["/vpn", "/log", "/shared"]

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
