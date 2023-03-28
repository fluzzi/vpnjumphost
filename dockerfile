FROM alpine:edge

COPY rootfs /

#RUN apk add -X https://nl.alpinelinux.org/alpine/edge/main -u alpine-keys --allow-untrusted
RUN apk add -X https://nl.alpinelinux.org/alpine/edge/testing -u alpine-keys --allow-untrusted

#RUN echo "@edge http://nl.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories
RUN echo "@edge http://nl.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
#Install software for vpn and proxy
RUN apk --update add --no-cache --upgrade \
  curl \
  openvpn \
  py3-setuptools \
  quagga \
  supervisor \
  openssh \
  busybox-extras \
  nmap \
  dnsmasq \
  openresolv \
  squid \
  openconnect \
  bash \
  inotify-tools



RUN mkdir /var/run/sshd
RUN mkdir /log
RUN mkdir /shared
RUN touch /log/supervisord.log
RUN touch /etc/dnsmasq-conf.conf
RUN touch /etc/dnsmasq-resolv.conf

RUN echo "root:root" | chpasswd
RUN sed -i s/#PermitRootLogin.*/PermitRootLogin\ yes/ /etc/ssh/sshd_config
RUN sed -i s/AllowTcpForwarding.*/AllowTcpForwarding\ yes/ /etc/ssh/sshd_config

COPY conf/supervisord.conf /etc/supervisord.conf
COPY authorized_keys /root/.ssh/authorized_keys
COPY conf/squid*.conf /etc/squid/
COPY conf/zebra.conf /etc/quagga/zebra.conf
COPY conf/ospfd.conf /etc/quagga/ospfd.conf
COPY conf/resolvconf.conf /etc
COPY conf/dnsmasq.conf /etc
COPY conf/openssl.conf /etc

RUN chmod 600 /root/.ssh/authorized_keys

EXPOSE 22
EXPOSE 3128
EXPOSE 53/udp

VOLUME ["/vpn", "/log", "/shared"]

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
