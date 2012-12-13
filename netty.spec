Name:           netty
Version:        3.5.11
Release:        2%{?dist}
Summary:        An asynchronous event-driven network application framework and tools for Java

Group:          Development/Libraries
License:        ASL 2.0
URL:            https://netty.io/
Source0:        https://github.com/downloads/%{name}/%{name}/%{name}-%{version}.Final-dist.tar.bz2

Patch0:         %{name}-port-to-jzlib-1.1.0.patch

BuildArch:      noarch

BuildRequires:  maven
BuildRequires:  maven-antrun-plugin
BuildRequires:  maven-assembly-plugin
BuildRequires:  maven-compiler-plugin
BuildRequires:  maven-enforcer-plugin
BuildRequires:  maven-javadoc-plugin
BuildRequires:  maven-plugin-bundle
BuildRequires:  maven-resources-plugin
BuildRequires:  maven-source-plugin
BuildRequires:  maven-surefire-plugin
BuildRequires:  ant-contrib

BuildRequires:  felix-osgi-compendium
BuildRequires:  felix-osgi-core
BuildRequires:  jboss-logging
BuildRequires:  jboss-marshalling
BuildRequires:  protobuf-java
BuildRequires:  slf4j
BuildRequires:  sonatype-oss-parent
BuildRequires:  tomcat-servlet-3.0-api

Requires:       java
Requires:       jpackage-utils
Requires:       protobuf-java

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
Summary:   API documentation for %{name}
Group:     Documentation
Requires:  jpackage-utils

%description javadoc
%{summary}.

%prep
%setup -q -n %{name}-%{version}.Final
# just to be sure, but not used anyway
rm -rf jar doc license

%pom_xpath_remove "pom:plugin[pom:artifactId[text()='maven-jxr-plugin']]"
%pom_xpath_remove "pom:plugin[pom:artifactId[text()='maven-checkstyle-plugin']]"
%pom_remove_plugin org.eclipse.m2e:lifecycle-mapping
%pom_remove_dep javax.activation:activation
%pom_remove_plugin :animal-sniffer-maven-plugin
%pom_xpath_remove "pom:execution[pom:id[text()='remove-examples']]"
%pom_xpath_remove "pom:plugin[pom:artifactId[text()='maven-javadoc-plugin']]/pom:configuration"

sed s/jboss-logging-spi/jboss-logging/ -i pom.xml

# Remove bundled jzlib and use system jzlib
rm -rf src/main/java/org/jboss/netty/util/internal/jzlib
%pom_add_dep com.jcraft:jzlib
sed -i s/org.jboss.netty.util.internal.jzlib/com.jcraft.jzlib/ \
    $(find src/main/java/org/jboss/netty/handler/codec -name \*.java | sort -u)
%patch0 -p1

%build
# skipping tests because we don't have easymockclassextension
mvn-rpmbuild -Dmaven.test.skip=true install javadoc:aggregate


%install
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}

install -m 644 target/%{name}-%{version}.Final.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pm 644 pom.xml $RPM_BUILD_ROOT/%{_mavenpomdir}/JPP-%{name}.pom

%add_maven_depmap -a org.jboss.netty:netty JPP-%{name}.pom %{name}.jar

%files
%doc LICENSE.txt NOTICE.txt
%{_javadir}/%{name}.jar
%{_mavendepmapfragdir}/%{name}
%{_mavenpomdir}/JPP-%{name}.pom

%files javadoc
%doc LICENSE.txt NOTICE.txt
%{_javadocdir}/%{name}

%changelog
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

* Thu Aug 15 2012 Tomas Rohovsky <trohovsk@redhat.com> - 3.5.4-1
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
