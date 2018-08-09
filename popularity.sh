#!/bin/bash

declare -a arr=("org.junit" "org.testng" "org.slf4j" "org.apache.log4j" "ch.qos.logback" "org.apache.commons.logging"
"org.pmw.tinylog" "com.netflix.blitz4j" "com.esotericsoftware.minlog" "com.google.common" "org.apache.commons.lang" "org.mockito" "org.easymock"
"org.powermock" "org.jmock" "org.bouncycastle" "org.apache.commons.crypto" "com.facebook.crypto" "com.intel.chimera"
"org.spongycastle" "org.keyczar" "com.android.org.conscrypt" "com.google.gson" "org.json.simple" "org.h2" "com.w11k.lsql" "org.apache.derby"
"org.apache.shiro" "org.springframework.security" "org.hibernate" "org.apache.ibatis" "com.j256.ormlite" "org.apache.xerces" "org.dom4j" "org.jdom"
"io.vertx.ext.mail" "org.apache.commons.mail" "org.apache.commons.collections" "it.unimi.dsi.fastutil" "org.mapdb" "com.carrotsearch.hppc"
"org.cliffc.high_scale_lib" "org.eclipse.collections" "com.facebook.util" "cc.mallet" "smile" "org.deeplearning4j" "moa" "de.lmu.ifi.dbs.elki"
"org.apache.mahout"
while IFS= read -r line
do
    cd "PopularityRepositories"
    git clone "$line"

    #junit4
    if grep -r --include '*.java' "org.junit" "$line";then
	
    fi
       
done < file


