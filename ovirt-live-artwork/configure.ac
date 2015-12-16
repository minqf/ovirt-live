#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.60])
define([VERSION_MAJOR], [1])
define([VERSION_MINOR], [0])
define([VERSION_FIX], [0])
define([VERSION_NUMBER], VERSION_MAJOR[.]VERSION_MINOR[.]VERSION_FIX)
define([VERSION_RELEASE], [1])
define([VERSION_SUFFIX], [])

AC_INIT([ovirt-live-artwork], [VERSION_NUMBER], [devel@ovirt.org])
PACKAGE_RPM_VERSION="VERSION_NUMBER"
PACKAGE_RPM_RELEASE="VERSION_RELEASE"
AC_SUBST([PACKAGE_RPM_VERSION])
AC_SUBST([PACKAGE_RPM_RELEASE])

AM_INIT_AUTOMAKE([foreign])

AC_CONFIG_FILES([
	Makefile
	ovirt-live-artwork.spec
	pixmaps/Makefile
	wallpapers/Makefile
	wallpapers/gnome/Makefile
	wallpapers/mate/Makefile
	wallpapers/normalish/Makefile
	wallpapers/standard/Makefile
	wallpapers/tv-wide/Makefile
	wallpapers/wide/Makefile
])
AC_OUTPUT