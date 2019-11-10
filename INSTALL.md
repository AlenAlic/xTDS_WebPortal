# xTDS WebPortal
Set up the xTDS WebPortal cluster, to run an ETDS and NTDS live version, a TEST version, and a DEV version.

Instructions for a standalone installation can be found in the STANDALONE.md file.






## Cluster installation (Ubuntu 18.04 LTS)

### Preparation


#### Mail
Before installing the cluster, it is advised you install the mailserver repository first, found at: [https://github.com/AlenAlic/mailserver](https://github.com/AlenAlic/mailserver) 

This will configure the server to be able to send and receive mail, something that the xTDS WebPortal needs. 

Follow the instructions there, then come back here to install the cluster.

Make sure the following email addresses are available:

- admin@xtds.nl
- etds@xtds.nl
- ntds@xtds.nl


#### DNS settings
In general, TLL values of 5 Min. (300 sec) are recommended.

Make sure you have the following DNS records available for the ETDS part:

|Name|Type|Value|INFO|
|---|---|---|---|
|@|A|\<your ipv4 adress\>|
|@|AAAA|\<your ipv6 adress\>|
|dev|CNAME|@|
|test|CNAME|@|

Make sure you have the following DNS records available for the NTDS part:

|Name|Type|Value|INFO|
|---|---|---|---|
|@|A|\<your ipv4 adress\>|
|@|AAAA|\<your ipv6 adress\>|
|portal|CNAME|@|



### Installer instance
We'll use an instance of the xTDS WebPortal to install the cluster.

    git clone https://github.com/AlenAlic/xTDS_WebPortal
    cd xTDS_WebPortal
    
From here you can run any of the installations located in the scripts folder.



### Variables
Before installing anything, set the following environment variables:

    export FLASK_APP=run.py
    export XTDS_DOMAIN=xtds.nl
    export NTDS_DOMAIN=portal.ntds.dance



### Installation scripts

#### Base items
To install all the base dependencies, run the `install_base` script.

    source scripts/install_base


#### ETDS
Before installing the ETDS version, set the following environment variables:

    export ETDS_EMAIL_PASSWORD=<password>
    export ETDS_DOMAIN=$XTDS_DOMAIN
    export ETDS_DB_PASSWORD=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
    export ETDS_SECRET_KEY=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
    export ETDS_FOLDER=ETDS
Then run the installation script:

    source scripts/install_ETDS
Finally, copy the `ETDS_DB_PASSWORD` and run the following command to create a login path for cronjobs to run backups:

    sudo mysql_config_editor set --login-path=etds --host=localhost --user=etds --password
When prompted, paste the password and press Enter.

    source scripts/install_ETDS
    
    
#### NTDS
Before installing the NTDS version, set the following environment variables:

    export NTDS_EMAIL_PASSWORD=<password>
    export NTDS_DOMAIN=$NTDS_DOMAIN
    export NTDS_DB_PASSWORD=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
    export NTDS_SECRET_KEY=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
    export NTDS_FOLDER=NTDS
Then run the installation script:

    source scripts/install_NTDS
Finally, copy the `NTDS_DB_PASSWORD` and run the following command to create a login path for cronjobs to run backups:

    sudo mysql_config_editor set --login-path=ntds --host=localhost --user=ntds --password
When prompted, paste the password and press Enter.


#### TEST
Before installing the TEST version, set the following environment variables:

    export TEST_DOMAIN=test.$XTDS_DOMAIN
    export TEST_DB_PASSWORD=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
    export TEST_SECRET_KEY=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
    export TEST_FOLDER=TEST
Then run the installation script:

    source scripts/install_TEST
Finally, copy the `TEST_DB_PASSWORD` and run the following command to create a login path for cronjobs to run backups:

    sudo mysql_config_editor set --login-path=test_xtds --host=localhost --user=test_xtds --password
When prompted, paste the password and press Enter.


#### DEV
Before installing the DEV version, set the following environment variables:

    export DEV_DOMAIN=dev.$XTDS_DOMAIN
    export DEV_DB_PASSWORD=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
    export DEV_SECRET_KEY=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
    export DEV_FOLDER=DEV
Then run the installation script:

    source scripts/install_DEV
Finally, copy the `DEV_DB_PASSWORD` and run the following command to create a login path for cronjobs to run backups:

    sudo mysql_config_editor set --login-path=dev_xtds --host=localhost --user=dev_xtds --password
When prompted, paste the password and press Enter.



### Backups
The cronjobs scripts have been generated in the `FOLDER/xTDS_WebPortal/cron/` folder.

To set the automatic backups, open the cronab:
    crontab -e

Append the following to the file, and uncomment the backups that you wish to use:

    # ETDS
    #0 * * * * ~/ETDS/xTDS_WebPortal/cron/hourly
    #@weekly ~/ETDS/xTDS_WebPortal/cron/weekly
    #*/5 * * * * ~/ETDS/xTDS_WebPortal/cron/tournament


    # NTDS
    #0 * * * * ~/NTDS/xTDS_WebPortal/cron/hourly
    #@weekly ~/NTDS/xTDS_WebPortal/cron/weekly
    #*/5 * * * * ~/NTDS/xTDS_WebPortal/cron/tournament
    
    
    # TEST
    #0 * * * * ~/TEST/xTDS_WebPortal/cron/hourly
    #@weekly ~/TEST/xTDS_WebPortal/cron/weekly
    
    
    # DEV
    #0 * * * * ~/DEV/xTDS_WebPortal/cron/hourly
    #@weekly ~/DEV/xTDS_WebPortal/cron/weekly

