distaff
=======

Simple system inventory, track your servers, how much ram, what packages, etc.
Written in python, with mongodb as a backend.
Limited functionality so far.


├── config
│   └── distaff.conf
├── LICENSE
├── Makefile
├── Makefile.common
├── packaging
│   ├── authors.sh
│   ├── deb
│   │   └── distaff.in
│   └── rpm
│       └── distaff.spec.in
├── README.md
└── src
    ├── gavage.py       Shove info into DB
    ├── hostscraper.py  Scrape info
    └── vmMonPoller.py  Pull info from opscode hosted chef

5 directories, 11 files

5 directories, 9 files
