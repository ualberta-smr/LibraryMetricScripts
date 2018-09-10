#!/bin/bash
#Description: This metric counts the number of client projects of the libraries defined in repositories.
#How to use: ./popularity search_results.txt
#Input: search_results (file with repositories whose source code will be searched for Java import statements)
#Output: popularity_results.txt (file which will have a line in the following format for each of the libraries)
#[library]:[number of client projects]
#

#To add a new library, add the prefix of the Java package here in the array of packages. 
declare -a packages=("org.junit" "org.testng" "org.slf4j" "org.apache.log4j" "ch.qos.logback" "org.apache.commons.logging"
"org.pmw.tinylog" "com.netflix.blitz4j" "com.esotericsoftware.minlog" "com.google.common" "org.apache.commons.lang" "org.mockito" "org.easymock"
"org.powermock" "org.jmock" "org.bouncycastle" "org.apache.commons.crypto" "com.facebook.crypto" "com.intel.chimera"
"org.spongycastle" "org.keyczar" "com.android.org.conscrypt" "com.google.gson" "org.json.simple" "org.h2" "com.w11k.lsql" "org.apache.derby"
"org.apache.shiro" "org.springframework.security" "org.hibernate" "org.apache.ibatis" "com.j256.ormlite" "org.apache.xerces" "org.dom4j" "org.jdom"
"io.vertx.ext.mail" "org.apache.commons.mail" "org.apache.commons.collections" "it.unimi.dsi.fastutil" "org.mapdb" "com.carrotsearch.hppc"
"org.cliffc.high_scale_lib" "org.eclipse.collections" "com.facebook.util" "cc.mallet" "smile" "org.deeplearning4j" "moa" "de.lmu.ifi.dbs.elki"
"org.apache.mahout")

#Add the repository of the library here
declare -a repositories=("junit-team/junit4"
"cbeust/testng"
"qos-ch/slf4j"
"apache/logging-log4j2"
"qos-ch/logback"
"apache/commons-logging"
"pmwmedia/tinylog"
"Netflix/blitz4j"
"EsotericSoftware/minlog"
"google/guava"
"apache/commons-lang"
"mockito/mockito"
"easymock/easymock"
"powermock/powermock"
"jmock-developers/jmock-library"
"bcgit/bc-java"
"apache/commons-crypto"
"facebook/conceal"
"intel-hadoop/chimera"
"rtyley/spongycastle"
"google/keyczar"
"google/conscrypt"
"google/gson"
"fangyidong/json-simple"
"h2database/h2database"
"w11k/lsql"
"apache/derby"
"apache/shiro"
"spring-projects/spring-security"
"hibernate/hibernate-orm"
"mybatis/mybatis-3"
"j256/ormlite-android"
"apache/xerces2-j"
"dom4j/dom4j"
"hunterhacker/jdom"
"vert-x3/vertx-mail-client"
"apache/commons-email"
"apache/commons-collections"
"vigna/fastutil"
"jankotek/mapdb"
"carrotsearch/hppc"
"stephenc/high-scale-lib"
"eclipse/eclipse-collections"
"facebook/jcommon"
"mimno/Mallet"
"haifengl/smile"
"deeplearning4j/deeplearning4j"
"Waikato/moa"
"elki-project/elki"
"apache/mahout")

#This array keeps track of the client project counts for each library. Make sure that this matches the number of repositories
declare -a counts=(0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)

if [ -f popularity_results.txt ]; then
    rm popularity_results.txt
fi

while IFS= read -r line
do
    cd "PopularityDataset"
    #echo "$line"
    mkdir "CurrentRepository"
    cd "CurrentRepository"
    git clone "$line"
    cd ..

    count=0
    for i in "${packages[@]}"
    do
	if grep -q -r --include '*.java' "import $i" "CurrentRepository";then
	    #echo "$i" >> popularity_results.txt
	    counts[$count]=$((${counts[$count]}+1))
	fi
	count=$((count+1))
    done
    rm -rf "CurrentRepository"
    cd ..
done < "$1"

count=0
for i in "${repositories[@]}"
do
    echo "$i:${counts[$count]}" >> popularity_results.txt
    count=$((count+1))
done

