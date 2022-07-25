%global debug_package %{nil}

%global __strip /bin/true

%global __brp_mangle_shebangs /bin/true

Name: atlassian-jira-core
Epoch: 100
Version: 8.20.11
Release: 1%{?dist}
Summary: Atlassian Jira Core
License: Apache-2.0
URL: https://www.atlassian.com/software/jira/core
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: chrpath
BuildRequires: fdupes
Requires(pre): shadow-utils
Requires: java

%description
Atlassian Jira Core is a project and task management solution built for
business teams.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%install
install -Dpm755 -d %{buildroot}%{_unitdir}
install -Dpm755 -d %{buildroot}/opt/atlassian/jira
cp -rfT jira %{buildroot}/opt/atlassian/jira
install -Dpm644 -t %{buildroot}%{_unitdir} jira.service
chmod a+x %{buildroot}/opt/atlassian/jira/bin/start-jira.sh
chmod a+x %{buildroot}/opt/atlassian/jira/bin/stop-jira.sh
find %{buildroot}/opt/atlassian/jira -type f -name '*.so' -exec chrpath -d {} \;
find %{buildroot}/opt/atlassian/jira -type f -name '*.bak' -delete
find %{buildroot}/opt/atlassian/jira -type f -name '*.orig' -delete
find %{buildroot}/opt/atlassian/jira -type f -name '*.rej' -delete
fdupes -qnrps %{buildroot}/opt/atlassian/jira

%check

%pre
set -euxo pipefail

JIRA_HOME=/var/atlassian/application-data/jira

if [ ! -d $JIRA_HOME -a ! -L $JIRA_HOME ]; then
    mkdir -p $JIRA_HOME
fi

if ! getent group jira >/dev/null; then
    groupadd \
        --system \
        jira
fi

if ! getent passwd jira >/dev/null; then
    useradd \
        --system \
        --gid jira \
        --home-dir $JIRA_HOME \
        --no-create-home \
        --shell /usr/sbin/nologin \
        jira
fi

chown -Rf jira:jira $JIRA_HOME
chmod 0750 $JIRA_HOME

%post
set -euxo pipefail

JIRA_CATALINA=/opt/atlassian/jira

chown -Rf jira:jira $JIRA_CATALINA
chmod 0700 $JIRA_CATALINA

%files
%license LICENSE
%dir /opt/atlassian
%{_unitdir}/jira.service
/opt/atlassian/jira

%changelog
