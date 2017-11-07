%{?scl:%scl_package netty}
%{!?scl:%global pkg_name %{name}}

# Disable generation of debuginfo package
%global debug_package %{nil}
%global namedreltag .Final
%global namedversion %{version}%{?namedreltag}

%bcond_without	jp_minimal

Name:		%{?scl_prefix}netty
Version:	4.1.13
Release:	1%{?dist}
Summary:	An asynchronous event-driven network application framework and tools for Java
License:	ASL 2.0
URL:		https://netty.io/
Source0:	https://github.com/%{pkg_name}/%{pkg_name}/archive/%{pkg_name}-%{namedversion}.tar.gz
# Upsteam uses a simple template generator script written in groovy and run with gmaven
# We don't have the plugin and want to avoid groovy dependency
# This script is written in bash+sed and performs the same task
Source1:	codegen.bash
Patch0:		0001-Remove-OpenSSL-parts-depending-on-tcnative.patch
Patch1:		0002-Remove-NPN.patch
Patch2:		0003-Remove-conscrypt-ALPN.patch

Buildrequires:	autoconf
Buildrequires:	automake
Buildrequires:	libtool
BuildRequires:	%{?scl_prefix_maven}maven-local
BuildRequires:	%{?scl_prefix_maven}ant-contrib
BuildRequires:	%{?scl_prefix}jzlib
BuildRequires:	%{?scl_prefix_java_common}apache-commons-logging
BuildRequires:	%{?scl_prefix_maven}maven-plugin-bundle
BuildRequires:	%{?scl_prefix}log4j
BuildRequires:	%{?scl_prefix_maven}maven-antrun-plugin
BuildRequires:	%{?scl_prefix_maven}maven-dependency-plugin
BuildRequires:  %{?scl_prefix_maven}maven-remote-resources-plugin
BuildRequires:	%{?scl_prefix_maven}maven-plugin-build-helper
BuildRequires:  %{?scl_prefix_maven}exec-maven-plugin
BuildRequires:	%{?scl_prefix}jetty-alpn-api
BuildRequires:	%{?scl_prefix_java_common}maven-hawtjni-plugin
BuildRequires:	%{?scl_prefix_java_common}javassist
BuildRequires:	%{?scl_prefix}jctools
BuildRequires:	%{?scl_prefix_java_common}slf4j%{?scl:-api}
BuildRequires:	%{?scl_prefix_maven}sonatype-oss-parent
%if %{without jp_minimal}
BuildRequires:	mvn(com.fasterxml:aalto-xml)
BuildRequires:	mvn(com.github.jponge:lzma-java)
BuildRequires:	mvn(com.google.protobuf.nano:protobuf-javanano)
BuildRequires:	mvn(com.google.protobuf:protobuf-java)
BuildRequires:	mvn(com.ning:compress-lzf)
BuildRequires:	mvn(net.jpountz.lz4:lz4)
BuildRequires:	mvn(org.bouncycastle:bcpkix-jdk15on)
BuildRequires:	mvn(org.jboss.marshalling:jboss-marshalling)
%endif
# transitive need to be added for scl
BuildRequires:	%{?scl_prefix}disruptor
BuildRequires:	%{?scl_prefix}jctools
BuildRequires:	%{?scl_prefix}jackson-core
BuildRequires:	%{?scl_prefix}jackson-databind
BuildRequires:	%{?scl_prefix}jackson-dataformat-yaml
BuildRequires:	%{?scl_prefix}jackson-dataformat-xml
BuildRequires:	%{?scl_prefix}jackson-annotations
BuildRequires:	%{?scl_prefix}jackson-module-jaxb-annotations
BuildRequires:	%{?scl_prefix_java_common}jansi
BuildRequires:	%{?scl_prefix}jeromq
BuildRequires:	%{?scl_prefix}apache-commons-csv
BuildRequires:	%{?scl_prefix}snakeyaml
%{!?scl:
BuildRequires:	mvn(kr.motd.maven:os-maven-plugin)
}
BuildRequires:	%{?scl_prefix_java_common}PyXB	
%{?scl:Requires: %scl_runtime}

%description
Netty is a NIO client server framework which enables quick and easy
development of network applications such as protocol servers and
clients. It greatly simplifies and streamlines network programming
such as TCP and UDP socket server.

'Quick and easy' doesn't mean that a resulting application will suffer
from a maintainability or a performance issue. Netty has been designed
carefully with the experiences earned from the implementation of a lot
of protocols such as FTP, SMTP, HTTP, and various binary and
text-based legacy protocols. As a result, Netty has succeeded to find
a way to achieve ease of development, performance, stability, and
flexibility without a compromise.

%package javadoc
Summary:	API documentation for %{name}

%description javadoc
%{summary}.

%prep
%setup -q -n %{pkg_name}-%{pkg_name}-%{namedversion}

%patch0 -p1
%patch1 -p1
%patch2 -p1

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
# Missing Mavenized rxtx
%pom_disable_module "transport-rxtx"
%pom_remove_dep ":netty-transport-rxtx" all
# Missing com.barchart.udt:barchart-udt-bundle:jar:2.3.0
%pom_disable_module "transport-udt"
%pom_remove_dep ":netty-transport-udt" all
%pom_remove_dep ":netty-build" all
# Not needed
%pom_disable_module "example"
%pom_remove_dep ":netty-example" all
%pom_disable_module "testsuite"
%pom_disable_module "testsuite-autobahn"
%pom_disable_module "testsuite-osgi"
%pom_disable_module "tarball"
%pom_disable_module "microbench"

%pom_xpath_inject 'pom:plugin[pom:artifactId="maven-remote-resources-plugin"]' '
<dependencies>
<dependency>
<groupId>io.netty</groupId>
<artifactId>netty-dev-tools</artifactId>
<version>${project.version}</version>
</dependency>
</dependencies>'

%pom_remove_plugin :maven-antrun-plugin
# get-jetty-alpn-agent
%pom_remove_plugin :maven-dependency-plugin
# style checker
%pom_remove_plugin :xml-maven-plugin
%pom_remove_plugin -r :maven-checkstyle-plugin
%pom_remove_plugin -r :animal-sniffer-maven-plugin
%pom_remove_plugin -r :maven-enforcer-plugin
%pom_remove_plugin -r :maven-shade-plugin
%pom_remove_plugin -r :maven-release-plugin
%pom_remove_plugin -r :maven-clean-plugin
%pom_remove_plugin -r :maven-source-plugin
%pom_remove_plugin -r :maven-deploy-plugin
%pom_remove_plugin -r :maven-jxr-plugin
%pom_remove_plugin -r :maven-javadoc-plugin
%pom_remove_plugin -r :forbiddenapis

cp %{SOURCE1} common/codegen.bash
%pom_add_plugin org.codehaus.mojo:exec-maven-plugin common '
<executions>
    <execution>
        <id>generate-collections</id>
        <phase>generate-sources</phase>
        <goals>
            <goal>exec</goal>
        </goals>
        <configuration>
            <executable>common/codegen.bash</executable>
        </configuration>
    </execution>
</executions>
'
%pom_remove_plugin :groovy-maven-plugin common

%if %{with jp_minimal}
%pom_remove_dep -r "com.google.protobuf:protobuf-java"
%pom_remove_dep -r "com.google.protobuf.nano:protobuf-javanano"
rm codec/src/main/java/io/netty/handler/codec/protobuf/*
sed -i '/import.*protobuf/d' codec/src/main/java/io/netty/handler/codec/DatagramPacket*.java
%pom_remove_dep -r "org.jboss.marshalling:jboss-marshalling"
rm codec/src/main/java/io/netty/handler/codec/marshalling/*
%pom_remove_dep -r org.bouncycastle
rm handler/src/main/java/io/netty/handler/ssl/util/BouncyCastleSelfSignedCertGenerator.java
sed -i '/BouncyCastleSelfSignedCertGenerator/s/.*/throw new UnsupportedOperationException();/' \
    handler/src/main/java/io/netty/handler/ssl/util/SelfSignedCertificate.java
%pom_remove_dep -r com.fasterxml:aalto-xml
%pom_disable_module codec-xml
%pom_remove_dep :netty-codec-xml all
%pom_remove_dep -r com.github.jponge:lzma-java
rm codec/src/*/java/io/netty/handler/codec/compression/Lzma*.java
%pom_remove_dep -r com.ning:compress-lzf
rm codec/src/*/java/io/netty/handler/codec/compression/Lzf*.java
%pom_remove_dep -r net.jpountz.lz4:lz4
rm codec/src/*/java/io/netty/handler/codec/compression/Lz4*.java

%endif # jp_minimal

# we want to build only netty-transport-native-epoll module in scl package
%{?scl:
%pom_xpath_remove "pom:build/pom:extensions"
%pom_disable_module "codec-haproxy"
%pom_disable_module "codec-http"
%pom_disable_module "codec-http2"
%pom_disable_module "codec-socks"
%pom_disable_module "handler-proxy"
%pom_disable_module "transport-sctp"
%pom_disable_module "all"
}

sed -i 's|taskdef|taskdef classpathref="maven.plugin.classpath"|' all/pom.xml

# workaround for the hawtjni issue
mkdir -p transport-native-epoll/src/main/native-package
touch transport-native-epoll/src/main/native-package/netty-transport-native-epoll.h

%pom_xpath_inject "pom:plugins/pom:plugin[pom:artifactId = 'maven-antrun-plugin']" '<dependencies><dependency><groupId>ant-contrib</groupId><artifactId>ant-contrib</artifactId><version>1.0b3</version></dependency></dependencies>' all/pom.xml
%pom_xpath_inject "pom:execution[pom:id = 'build-native-lib']/pom:configuration" '<verbose>true</verbose>' transport-native-epoll/pom.xml

# Upstream has jctools bundled.
%pom_xpath_remove "pom:build/pom:plugins/pom:plugin[pom:artifactId = 'maven-bundle-plugin']/pom:executions/pom:execution[pom:id = 'generate-manifest']/pom:configuration/pom:instructions/pom:Import-Package" common/pom.xml

# Tell xmvn to install attached artifact, which it does not
# do by default. In this case install all attached artifacts with
# the linux classifier.
%mvn_package ":::linux*:"
%{?scl:EOF}

%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
export CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="$RPM_LD_FLAGS"
%mvn_build -f
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install
%{?scl:EOF}

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%changelog
* Mon Nov 06 2017 Auusto Mecking Caringi <acaringi@redhat.com> - 4.1.13-1
- Update to upstream version 4.1.13

* Wed Mar 29 2017 Tomas Repik <trepik@redhat.com> - 4.0.42-5
- Keep Import-Package default value
- scl conversion

* Thu Mar 16 2017 Michael Simacek <msimacek@redhat.com> - 4.0.42-4
- Remove maven-javadoc-plugin from POM

* Wed Mar 15 2017 Michael Simacek <msimacek@redhat.com> - 4.0.42-3
- Add jp_minimal conditional

* Mon Feb 06 2017 Michael Simacek <msimacek@redhat.com> - 4.0.42-2
- Remove useless plugins

* Thu Oct 20 2016 Severin Gehwolf <sgehwolf@redhat.com> - 4.0.42-1
- Remove old netty4 provides/obsoletes.

* Thu Oct 20 2016 Severin Gehwolf <sgehwolf@redhat.com> - 4.0.42-1
- Update to upstream 4.0.42 release.
- Resolves RHBZ#1380921

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.28-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.28-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 20 2015 Severin Gehwolf <sgehwolf@redhat.com> - 4.0.28-1
- Update to upstream 4.0.28 release.
- Fixes CVE-2015-2156 (HttpOnly cookie bypass).
- Resolves RHBZ#1111502

* Wed May 20 2015 Severin Gehwolf <sgehwolf@redhat.com> - 4.0.27-1
- Update to upstream 4.0.27 release.

* Wed Apr 01 2015 Severin Gehwolf <sgehwolf@redhat.com> - 4.0.19-3
- Drop mvn(org.easymock:easymockclassextension) BR.
  Resolves: RHBZ#1207991

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.19-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jun  9 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 4.0.19-1
- Update to upstream version 4.0.19
- Convert to arch-specific package

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.14-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Mar 04 2014 Stanislav Ochotnicky <sochotnicky@redhat.com> - 4.0.14-4
- Use Requires: java-headless rebuild (#1067528)

* Mon Jan 13 2014 Marek Goldmann <mgoldman@redhat.com> - 4.0.14-3
- Enable netty-all.jar artifact

* Mon Jan 13 2014 Marek Goldmann <mgoldman@redhat.com> - 4.0.14-2
- Bump the release, so Obsoletes work properly

* Mon Dec 30 2013 Marek Goldmann <mgoldman@redhat.com> - 4.0.14-1
- Upstream release 4.0.14.Final

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu May 16 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.6-1
- Update to upstream version 3.6.6

* Wed Apr 10 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.5-1
- Update to upstream version 3.6.5

* Mon Apr  8 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.4-1
- Update to upstream version 3.6.4

* Wed Feb 27 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.3-3
- Set scope of optional compile dependencies to 'provided'

* Wed Feb 27 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.3-2
- Drop dependency on OSGi
- Resolves: rhbz#916139

* Mon Feb 25 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.3-1
- Update to upstream version 3.6.3

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 3.6.2-2
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Wed Jan 16 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.2-1
- Update to upstream version 3.6.2

* Tue Jan 15 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.1-1
- Update to upstream version 3.6.1

* Thu Dec 13 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.11-2
- Use system jzlib instead of bundled jzlib
- Resolves: rhbz#878391

* Mon Dec  3 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.11-1
- Update to upstream version 3.5.11

* Mon Nov 12 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.10-1
- Update to upstream version 3.5.10

* Thu Oct 25 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.9-1
- Update to upstream version 3.5.9

* Fri Oct  5 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.8-1
- Update to upstream version 3.5.8

* Fri Sep  7 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.7-1
- Update to upstream version 3.5.7

* Mon Sep  3 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.6-1
- Update to upstream version 3.5.6

* Thu Aug 23 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.5-1
- Update to upstream version 3.5.5

* Wed Aug 15 2012 Tomas Rohovsky <trohovsk@redhat.com> - 3.5.4-1
- Update to upstream version 3.5.4

* Tue Jul 24 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.3-1
- Update to upstream version 3.5.3

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul 16 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.2-2
- Add additional depmap for org.jboss.netty:netty
- Fixes #840301

* Thu Jul 12 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.2-1
- Update to upstream version 3.5.2
- Convert patches to POM macros
- Enable jboss-logging

* Fri May 18 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.2.4-4
- Add enforcer-plugin to BR

* Wed Apr 18 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.2.4-3
- Remove eclipse plugin from BuildRequires

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Dec  5 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.2.4-1
- Update to latest upstream version

* Mon Jul 4 2011 Alexander Kurtakov <akurtako@redhat.com> 3.2.3-4
- Fix FTBFS.
- Adapt to current guidelines.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 17 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.2.3-2
- Use maven 3 to build
- Drop ant-contrib depmap (no longer needed)

* Thu Jan 13 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.2.3-1
- Initial version of the package
