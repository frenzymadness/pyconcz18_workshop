# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "generic/fedora27"

  config.vm.network "forwarded_port", guest: 8123, host: 8123
  config.vm.network "forwarded_port", guest: 1883, host: 1883

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # config.vbguest.installer_arguments = ['--nox11', '-- --do']

  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    # Packages installation
    sudo dnf install -y mosquitto

    # Disable Selinux
    sudo echo -e "SELINUX=disabled\nSELINUXTYPE=targeted" > /etc/sysconfig/selinux

    # MQTT service
    sudo systemctl enable mosquitto
    sudo systemctl start mosquitto

    # Home Assistant installation
    sudo chmod 777 /srv
    cd /srv
    python3 -m venv homeassistant
    cd homeassistant
    source bin/activate
    python3 -m pip install -U pip
    python3 -m pip install wheel paho-mqtt
    python3 -m pip install homeassistant

    sudo dd of=/etc/systemd/system/home-assistant@vagrant.service << EOF
[Unit]
Description=Home Assistant
After=network-online.target

[Service]
Type=simple
User=%i
ExecStart=/srv/homeassistant/bin/hass -c "/home/vagrant/.homeassistant"

[Install]
WantedBy=multi-user.target
EOF

    # Home Assistant service
    sudo systemctl --system daemon-reload
    sudo systemctl enable home-assistant@vagrant
    sudo systemctl start home-assistant@vagrant

    # Firewall
    sudo firewall-cmd --permanent --add-port=8123/tcp
    sudo firewall-cmd --permanent --add-port=1883/tcp
    sudo firewall-cmd --reload
  SHELL
end
