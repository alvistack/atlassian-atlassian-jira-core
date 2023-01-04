# Copyright 2022 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%global __strip /bin/true

%global __brp_mangle_shebangs /bin/true

Name: atlassian-jira-core
Epoch: 100
Version: 8.20.14
Release: 1%{?dist}
Summary: Atlassian Jira Core
License: Apache-2.0
URL: https://www.atlassian.com/software/jira/core
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: -post-build-checks
Requires(pre): chrpath
Requires(pre): fdupes
Requires(pre): patch
Requires(pre): shadow-utils
Requires(pre): wget

%description
Atlassian Jira Core is a project and task management solution built for
business teams.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%install
install -Dpm755 -d %{buildroot}%{_unitdir}
install -Dpm755 -d %{buildroot}/opt/atlassian/jira
install -Dpm644 -t %{buildroot}%{_unitdir} jira.service
install -Dpm644 -t %{buildroot}/opt/atlassian/jira atlassian-jira-core.patch

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

JIRA_DOWNLOAD_URL=http://product-downloads.atlassian.com/software/jira/downloads/atlassian-jira-core-8.20.14.tar.gz
JIRA_DOWNLOAD_DEST=/tmp/atlassian-jira-core-8.20.14.tar.gz
JIRA_DOWNLOAD_CHECKSUM=8240dba800b0e001851b1f32ee07e80f09cf64bbed71a2366a90853bff555d42

JIRA_CATALINA=/opt/atlassian/jira

wget -c $JIRA_DOWNLOAD_URL -O $JIRA_DOWNLOAD_DEST
echo -n "$JIRA_DOWNLOAD_CHECKSUM $JIRA_DOWNLOAD_DEST" | sha256sum -c -

mkdir -p $JIRA_CATALINA
find $JIRA_CATALINA -mindepth 1 | grep -v atlassian-jira-core.patch | xargs rm -rf || echo $?
tar zxf $JIRA_DOWNLOAD_DEST -C $JIRA_CATALINA --strip-components=1

cat $JIRA_CATALINA/atlassian-jira-core.patch | patch -p1
chmod a+x $JIRA_CATALINA/bin/start-jira.sh
chmod a+x $JIRA_CATALINA/bin/stop-jira.sh
find $JIRA_CATALINA -type f -name '*.so' -exec chrpath -d {} \;
find $JIRA_CATALINA -type f -name '*.bak' -delete
find $JIRA_CATALINA -type f -name '*.orig' -delete
find $JIRA_CATALINA -type f -name '*.rej' -delete
fdupes -qnrps $JIRA_CATALINA

chown -Rf jira:jira $JIRA_CATALINA
chmod 0700 $JIRA_CATALINA

%files
%license LICENSE
%dir /opt/atlassian
%dir /opt/atlassian/jira
%{_unitdir}/jira.service
/opt/atlassian/jira/atlassian-jira-core.patch

%changelog
