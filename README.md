# conti-project

## Project - Create POC for a Consultant time-management assignment

### Project group: Jesse, Josefine, Juaquin

# order of operation:

**Creation: Databse creation azure psql, Azure keyvault, VM 1 and 2 creation Storage container, Resource group.**

Database has two tables, one for consultant/names and one for consultant hours

Azure keyvault created and connected

identieties created for communication between VM, Keyvault, Storage

VM: Cloned git repo for access to program SSH key used for remote access

**Postman**

Start postman connection

**Time managment softar VM 1**

Time management software runs a few functions and calculates total work hour and saldo for day based on consultant input

**Insert cycoppg2**

Uploads processed consultant data to database in clouduploads consultant data to database in cloud

**Trigger report creation / report form VM 2**

Trough postman trigger report from report VM or Trigger report from manualtrigger.py runs the function

**Queries from DB to reporting software**

**Upload to pythonsdk**

uploads the created file to azure blob storage, using autoincrementation to individualize documents

**Finishes report in Azure blob container**

**End user can fetch report from azure**

# Project workflow and division

The project was divided up into sections where the group worked in paralell on different parts of the flow.Postman connection - Juaquin
Database and psycopg2 functions for time maangement - Jesse
Report query - Josefine

responsibilities where shared between team members, so overflow for merge conflict solution and additionall functions where done in group.

**git**. workflow: divided the development in dev branches that merged into a merge branch before being commited into main, to ensure the main is working.
