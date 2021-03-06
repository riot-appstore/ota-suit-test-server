FROM ubuntu:xenial

MAINTAINER Joakim Nohlgård <joakim.nohlgard@eistec.se>

ENV DEBIAN_FRONTEND noninteractive

# The following package groups will be installed:
# - upgrade all system packages to latest available version
# - native platform development and build system functionality (about 400 MB installed)
# - Cortex-M development (about 550 MB installed), through the gcc-arm-embedded PPA
# - MSP430 development (about 120 MB installed)
# - AVR development (about 110 MB installed)
# - LLVM/Clang build environment (about 125 MB installed)
# - x86 bare metal emulation (about 125 MB installed) (this pulls in all of X11)
# All apt files will be deleted afterwards to reduce the size of the container image.
# This is all done in a single RUN command to reduce the number of layers and to
# allow the cleanup to actually save space.
# Total size without cleaning is approximately 1.525 GB (2016-03-08)
# After adding the cleanup commands the size is approximately 1.497 GB
RUN \
    dpkg --add-architecture i386 >&2 && \
    echo 'Adding gcc-arm-embedded PPA' >&2 && \
    echo "deb http://ppa.launchpad.net/team-gcc-arm-embedded/ppa/ubuntu xenial main" \
     > /etc/apt/sources.list.d/gcc-arm-embedded.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 \
    --recv-keys B4D03348F75E3362B1E1C2A1D1FAA6ECF64D33B0 && \
    echo 'Upgrading all system packages to the latest available versions' >&2 && \
    apt-get update && apt-get -y dist-upgrade \
    && echo 'Installing native toolchain and build system functionality' >&2 && \
    apt-get -y install \
        bsdmainutils \
        build-essential \
        ccache \
        coccinelle \
        curl \
        cppcheck \
        doxygen \
        gcc-multilib \
        gdb \
        g++-multilib \
        git \
        graphviz \
        libpcre3 \
        parallel \
        pcregrep \
        python \
        python-pip \
        python3-pip \
        python3 \
        python3-pexpect \
        python3-crypto \
        python3-pyasn1 \
        python3-ecdsa \
        python3-flake8 \
        p7zip \
        software-properties-common \
        subversion \
        unzip \
        vim-common \
        wget \
    && echo 'Installing Cortex-M toolchain' >&2 && \
    apt-get -y install \
        gcc-arm-embedded \
    && echo 'Installing MSP430 toolchain' >&2 && \
    apt-get -y install \
        gcc-msp430 \
    && echo 'Installing AVR toolchain' >&2 && \
    apt-get -y install \
        gcc-avr \
        binutils-avr \
        avr-libc \
    && echo 'Installing LLVM/Clang toolchain' >&2 && \
    apt-get -y install \
        llvm \
        clang \
    && echo 'Installing x86 bare metal emulation' >&2 && \
    apt-get -y install \
        qemu-system-x86 \
    && echo 'Installing socketCAN' >&2 && \
    apt-get -y install \
        libsocketcan-dev:i386 \
        libsocketcan2:i386 \
    && echo 'Cleaning up installation files' >&2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install CMake 3.10
RUN wget -q https://cmake.org/files/v3.10/cmake-3.10.0.tar.gz -O- \
    | tar -C /tmp -xz && cd /tmp/cmake-3.10.0/ && ./bootstrap && \
    make && make install && cd && rm -rf /tmp/cmake-3.10.0

# Install MIPS binary toolchain
RUN mkdir -p /opt && \
        wget -q https://codescape.mips.com/components/toolchain/2016.05-03/Codescape.GNU.Tools.Package.2016.05-03.for.MIPS.MTI.Bare.Metal.CentOS-5.x86_64.tar.gz -O- \
        | tar -C /opt -xz

ENV PATH $PATH:/opt/mips-mti-elf/2016.05-03/bin
ENV MIPS_ELF_ROOT /opt/mips-mti-elf/2016.05-03

# Install RISC-V binary toolchain
RUN mkdir -p /opt && \
        wget -q https://github.com/gnu-mcu-eclipse/riscv-none-gcc/releases/download/v7.2.0-2-20180110/gnu-mcu-eclipse-riscv-none-gcc-7.2.0-2-20180111-2230-centos64.tgz -O- \
        | tar -C /opt -xz

# HACK download arch linux' flex dynamic library
RUN wget -q https://sgp.mirror.pkgbuild.com/core/os/x86_64/flex-2.6.4-2-x86_64.pkg.tar.xz -O- \
        | tar -C / -xJ usr/lib/libfl.so.2.0.0
RUN ldconfig
ENV PATH $PATH:/opt/gnu-mcu-eclipse/riscv-none-gcc/7.2.0-2-20180111-2230/bin

ENV APP_USER user
ENV APP_ROOT /code

#ENV C_FORCE_ROOT true # intentionally kept it commented


RUN mkdir /home/${APP_USER}
RUN mkdir /raw
RUN groupadd -r ${APP_USER} \
    && useradd -r -m \
    --home-dir /home/${APP_USER} \
    -s /usr/sbin/nologin \
    -g ${APP_USER} ${APP_USER}

RUN chown -R ${APP_USER} /home/${APP_USER}
RUN chown -R ${APP_USER} /raw

ADD ./RIOT_OTA_PoC /RIOT
#RUN chown -R ${APP_USER} /RIOT
#

COPY requirements.txt /code/
WORKDIR ${APP_ROOT}

RUN apt-get update
RUN apt-get install -y libssl-dev
RUN pip3 install -r requirements.txt

#USER ${APP_USER}
RUN touch /home/${APP_USER}/.gitconfig
RUN git config --global user.name "RIOT"
RUN git config --global user.email "riot@riot-os.org"
# Use an official Python runtime as a parent image
#FROM python:3.5
#
## Set the working directory to /app
#WORKDIR /app
#
## Copy the current directory contents into the container at /app
#ADD . /app
## Install any needed packages specified in requirements.txt
#RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME World

# Run app.py when the container launches
#WORKDIR /app/suit-server
#CMD ["python", "main.py"]
