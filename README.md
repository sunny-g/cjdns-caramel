Caramel
=======

A graphical user interface for managing [CJDNS](https://github.com/cjdelisle/cjdns) using GTK+. Right now it is very work-in-progress.

Screenshot
----------

![Screenshot of main window](http://cloud.github.com/downloads/duncanpk/cjdns-caramel/screenshot-2.png)

Dependencies
------------

Caramel requires Python 3 and bindings for gobject-introspection:

    sudo apt-get install python3 python3-gi

Usage
-----

Just clone this repository and run:

    python3 caramel.py

Configuration
-------------

Caramel maintains its own CJDNS configuration file at `~/.config/cjdroute.conf`.

During the first run, you will be asked to locate your CJDNS directory. If you have already have a *cjdroute.conf*, it will be copied over. Otherwise a new *cjdroute.conf* will be generated for you.
