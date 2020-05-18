FROM alpine:edge

COPY rootfs /

RUN apk --update add --no-cache \
  curl \
  openvpn \
  supervisor \
  openssh


RUN apk --update --allow-untrusted --repository http://dl-4.alpinelinux.org/alpine/edge/testing/ add       bash       openconnect && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

RUN mkdir /var/run/sshd
RUN mkdir /log
RUN touch /log/supervisord.log

RUN echo "root:root" | chpasswd
RUN sed -i s/#PermitRootLogin.*/PermitRootLogin\ yes/ /etc/ssh/sshd_config
RUN sed -i s/AllowTcpForwarding.*/AllowTcpForwarding\ yes/ /etc/ssh/sshd_config

COPY supervisord.conf /etc/supervisord.conf
COPY authorized_keys /root/.ssh/authorized_keys

RUN chmod 600 /root/.ssh/authorized_keys

EXPOSE 22

VOLUME ["/vpn", "/log"]

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
