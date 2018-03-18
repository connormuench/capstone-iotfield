# README

## Component Version Info

__Ruby:__ 2.3.3

__Rails:__ 5.1.4

__Postgres:__ 10.1

## Setup

This repository should already be cloned. If it hasn't been, do that now.

### Installing Prerequisites

Install at least the versions of [Ruby](https://rubyinstaller.org/), [Rails](http://railsinstaller.org/en), and [Postgres](https://www.postgresql.org/download/) listed in the Component Version Info section. The Rails installer can install the appropriate version of Ruby automatically.

Navigate to the 'webapp' directory within the cloned repository in a terminal and run `bundle install`. The bundler should automatically install all of the required Gems for the application to work.

__Note:__ On Windows, the `bcrypt` Gem is often installed incorrectly. Run `gem list bcrypt` and ensure that the x86-mingw32 version is not installed. If it is, run `gem uninstall bcrypt` to remove it and manually install the correct version using `gem install bcrypt --platform=ruby`.

### Setting Up the Database

The database needs to have a user that the web server can use to access it. Navigate to the `bin` directory within the Postgres installation directory and run `createuser -U postgres -P -s rails`. This command will prompt for the password for the `postgres` user, so enter whatever was set in the installation of Postgres. You will then be prompted for the password of the new user.

Navigate back to the `webapp` directory of the cloned repository in a terminal. Set the `WEBAPP_DATABASE_PASSWORD` environment variable to the password for the `rails` user created in Postgres. In Unix, this is just `WEBAPP_DATABASE_PASSWORD=<password>`, and in Windows the command is `set WEBAPP_DATABASE_PASSWORD=<password>`. Run `rails db:create` afterwards to create the database, and then `rails db:migrate` to set up the tables in the database.

__Note:__ After pulling changes from the repository in the future, only run `bundle install` and `rails db:migrate` to apply any new changes to the installed Gems and database. `rails db:migrate` does not initialize the database, only updates the tables, so previous data will not be lost (unless the migration explicitly removes a column from a table, for example).

### Starting the Web Server

From a terminal within the `webapp` directory of the cloned repository (make sure the environment variables are set if using a different terminal instance than the previous step), run `rails c` to start up the Rails console. We need to add an initial administrator manually, since the web application (intentionally) does not permit anyone to register an account on their own. Run the following command, substituting the values within angle brackets appropriately: `User.create!(username: <username>, email: <email>, password: <password>, password_confirmation: <password>, name: <name>, is_admin: true)`. A new administrator should be created. Run `exit` to close the console.

Run `rails s` to start the web server. This will start the web server on `localhost:3000`, listening on all IP addresses. The URL of the site depends on which network the client device is on:

* Same machine as the web server: `localhost:3000`.
* Different machine, same local network: `<IP address of host>:3000`.
* Different machine, different network (typical user on the Internet): 
  * If the host has its own public IP: `<Public IP of host>:3000`. The operating system's firewall may need to be set up to allow network traffic through this port.
  * If the host does not have its own public IP (like a home network), the network's router needs to set up to forward port 3000 for the host device. Consult the documentation of your particular router to accomplish this. The URL of the site will then be `<Public IP of network>:3000`.

__Note:__ The server will eventually be set up to run on port 80 in deployment, so users of the site won't have to mention the port number in the web address (as HTTP defaults to port 80). For the purposes of development, though, this setup is fine.
