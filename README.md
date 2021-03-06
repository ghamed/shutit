

[ShutIt](http://shutit.tk)
===============
Complex Docker Builds Made Simple

ShutIt is a tool for managing your build process that is both structured and flexible:

Structured:

- Modular structure
- Manages the startup and setup of your container ready for the build
- Has a lifecycle that can manage different parts of the lifecycle, eg:
	- Pre-requisites check
	- "Already installed?" check
	- Gather config
	- Start module
	- Stop module
	- Test module
	- Finalize container
- Allows you to set config
- Allows you to manage modules per distro (if needed)
- Forces you to define an order for the modules
- Puts record of build process into container
- Enables continuous regression testing

Flexible:

- Modules model shell interactions, with all the freedom and control that implies
- Modules can be plugged together like legos
- GUI allows to you build and download images for your own needs (see http://shutit.tk)
- Module scripts are in python, allowing full language control
- Many helper functions for common interaction patterns
- Can pause during build or on error to interact, then continue with build


REALLY QUICK START
------------------

See here:

http://ianmiell.github.io/shutit/

INSTALLATION
------------

See [INSTALL](http://github.com/ianmiell/shutit/blob/master/INSTALL.md)


WHAT DOES IT DO?
----------------
We start with a "Unit of Build", similar to a Dockerfile.

Unit of Build for Mongodb:

```
module:com.mycorp.mongo.mongodb
run order: 1234.1234
|---------------------------------------------------------------------------------------------------------------------------|
|apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10                                                               |
|echo "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen" | tee -a /etc/apt/sources.list.d/10gen.list  |
|apt-get update                                                                                                             |
|apt-get -y install apt-utils                                                                                               |
|apt-get -y install mongodb-10gen                                                                                           |
|---------------------------------------------------------------------------------------------------------------------------|
```

We call this a ShutIt module. In this case, we'll give this the id: 

```
com.mycorp.mongo.mongodb
```

and the run order

```
1234.1234
```

Say we want to plug these together with other modules. ShutIt allows you do this.

But what if one module depends on another, eg mymongomodule which trivially adds a line to a config?

Unit of Build for MyMongoDB (com.mycorp.mongo.mymongodb):

```
module: com.mycorp.mongo.mymongodb
run order: 1235.1235
|-----------------------------------------------|
|(depend on com.mycorp.mongo.mongodb)           |
|echo "config item" >> /etc/somewhere/somefile  |
|-----------------------------------------------|
```

and give it a run order of 1235.1235. Note that the run order is higher, as we depend on the com.mycorp.mongo.mongodb module being there (ShutIt checks all this for you).

As you plug together more and more modules, you'll find you need a build lifecycle to manage how these modules interact and build.

What ShutIt does to manage this is:

- gathers all the modules it can find in its path and determines their ordering
- for all modules, it gathers any build-specific config (e.g. passwords etc.)
- it checks dependencies and conflicts across all modules and figures out which modules need to be built
- for all modules, it checks whether the module is already installed
- for all modules, if it needs building, it runs the build
- for all modules, run a test cycle to ensure everything is as we expect
- for all modules, run a finalize function to clean up the container
- do any configured committing, tagging and pushing of the image

These correspond to the various functions that can be implemented.

ShutIt provides a means for auto-generation of modules (either bare ones, or from existing Dockerfiles) with:

```
shutit skeleton [-d Dockerfile] <directory to create module in> <domain>
```

eg:

```
shutit skeleton /home/me/shutit_modules/com/mycorp/mongo com.mycorp
```


CAN I CONTRIBUTE?
-----------------

We always need help, and with a potentially infinite number of libraries required, it's likely you will be able to contribute. Just mail ian.miell@gmail.com if you want to be assigned a mentor. [He won't bite](https://www.youtube.com/watch?v=zVUPmmUU3yY) 

Mailing List
------------
https://groups.google.com/forum/#!forum/shutit-users
shutit-users@groups.google.com

Dependencies
--------------
- python 2.7+
- See [here](https://gist.github.com/ianmiell/947ff3fabc44ace617c6) for a minimal build.

apt-get install git python-bottle docker.io python-pexpect
git clone https://github.com/ianmiell/shutit.git && cd shutit


Videos:
-------

- [Talk on ShutIt](https://www.youtube.com/watch?v=zVUPmmUU3yY) 

- [Setting up a ShutIt server in 3 minutes](https://www.youtube.com/watch?v=ForTMTUMp3s)

- [Steps for above](https://gist.github.com/ianmiell/947ff3fabc44ace617c6)

- [Configuring and uploading a MySql container](https://www.youtube.com/watch?v=snd2gdsEYTQ)

- [Building a win2048 container](https://www.youtube.com/watch?v=Wagof_wnRRY) cf: [Blog](http://zwischenzugs.wordpress.com/2014/05/09/docker-shutit-and-the-perfect-2048-game/)



Docs:
-----

- [Walkthrough](http://ianmiell.github.io/shutit/)




REALLY QUICK OVERVIEW
---------------------
You'll be interested in this if you:

- Want to take your scripts and turn them into stateless containers quickly,
without needing to learn or maintain a configuration management solution.

- Are a programmer who wants highly configurable containers for
differing use cases and environments.

- Find dockerfiles a great idea, but limiting in practice.

- Want to build stateless containers for production.

- Are interested in "phoenix deployment" using Docker.

I WANT TO SEE EXAMPLES
----------------------
See in ```library/*```
eg
```
cd library/mysql
./build.sh
./run.sh
```

Overview
--------
While evaluating Docker for my [corp](http://www.openbet.com) I reached a point where
using Dockerfiles was somewhat painful or verbose for complex and/or long and/or
configurable interactions. So we wrote our own.

ShutIt works in the following way:

- It runs a docker container (base image configurable)
- Within this container it runs through configurable set of modules (each with
  a globally unique module id) that runs in a defined order with a standard
  lifecycle:
     - dependency checking
     - conflict checking
     - remove configured modules
     - build configured modules
     - tag (and optionally push) configured modules (to return to that point
       of the build if desired)
     - test
     - finalize module ready for closure (ie not going to start/stop anything)
     - tag (and optionally push) finished container
- These modules must implement an abstract base class that forces the user to
  follow a lifecycle (like many test frameworks)
- It's written in python
- It's got a bunch of utility functions already written, eg:
     - pause_point (stop during build and give shell until you decide to 
       return to the script (v useful for debugging))
     - add_line_to_file (if line is not already there)
     - add_to_bashrc (to add something to everyone's login)
     - setup_prompt (to handle shell prompt oddities in a 
       reliable/predictable way)
     - is user_id_available
     - set_password (package-management aware)
     - file_exists
     - get_file_perms
     - package_installed (determine whether package is already installed)
     - loads more to come

If you have an existing bash script it is relatively trivial to port to this 
to get going with docker and start shipping containers (see create\_skeleton.sh
below). You can also use this to prototype builds before porting to whatever
configuration management tool you ultimately choose.

As a by-product of this design, you can use it in a similar way to chef/puppet
(by taking an existing container and configuring it to remove and build a
specific module), but it's not designed primarily for this purpose.

Chef/Puppet were suggested as alternatives, but for several reasons I didn't go
with them:

- I had to deliver something useful, and fast (spare time evaluation), so 
  taking time out to learn chef was not an option
- It struck me that what I was trying to do was the opposite of what chef is
  trying to do, ie I'm building static containers for a homogeneous environment
  rather than defining state for a heterogeneous machine estate and hoping
  it'll all work out
- I was very familiar with (p)expect, which was a good fit for this job and
  relatively easy to debug
- Anecdotally I'd heard that chef debugging was painful ("It works 100% of the
  time 60% of the time")
- I figured we could move quite easily to whatever CM tool was considered
  appropriate once we had a deterministic set of steps that also documented
  server requirements

If you are a sysadmin looking for something to manage dynamic, moving target
systems stick with chef/puppet. If you're a programmer who wants to manage a
bunch of existing scripts in a painless way, keep on reading.


# ShutIt User Guide

## Design goals

ShutIt was built originally to facilitate the deployment of complex Docker containers, so that developers can quickly prototype builds in a structured and flexible way with as shallow a learning curve as possible.

A ShutIt build is a programmable way of managing builds by modelling shell interactions.


## Key concepts
	
### Build

A ShutIt build consists of all the modules available going through the ShutIt Build lifecycle. This results in a container in a state from which it can be tagged, saved, exported, and/or pushed depending on your configuration.

### Module

A ShutIt module is a directory containing the configuration for the setup of a discrete unit of configuration.

This can be as simple as an apt-get install, a sequence of steps to get your package configured correctly, or a series of steps to set up networking for the a build, or anything else you deem useful to encapsulate as part of your build.

A module must inherit from ShutItModule and implement, as a mimimum, "is_installed" and "build" methods.

Each module has several attributes whose implications should be understood as they handle build order and dependency management:

#### module_id

A string - which should be globally unique - that represents this module's place in the ShutIt universe. By convention this follows the Java namespacing model of domain_name.namespace.module, eg

com.openbet.web.application

#### run_order

A float which represents the order in which this should be run in the ShutIt universe. 

The integer part should be a hash (in util.get_hash(string))of the domain used within themodule_id, eg com.openbet hashes to 1003189494. This is autogenerated by the "shutit skeleton" command (see below), which takes the domain as an argument.

The decimal part should be the order in which this module should be run within that ShutIt domain. 

This allows you to define a specific build order that is predictable.

#### description

Free text description of the module's purpose.

#### depends

List of module_ids of modules that are pre-requisites of this module.

#### conflicts

List of module_ids of modules that conflict with this module.


 

### ShutIt Build Lifecycle

#### Details

- Gather modules

Searches the modules directories given in the -m/--shutit_modules_dir argument for valid .py files to consider as part of the build.

- Gather configuration

Configuration is gathered in the following order:

1) Defaults loaded within the code

2) The following (auto-created) file is searched for: ~/.shutit/config 

This file can contain host-specific overrides, and is optional

3) configs/build.cnf is loaded from the current working directory of the shutit invocation

4) 0-n config files passed in with --config arguments are loaded

5) Command-line overrides, eg "-s com.mycorp.mymodule.module name value"

All config files need to have permissions 0x00.

- Check for conflicts

Module dependencies are checked to see whether there are any marked conflicts

- Check ready on all modules

Allows modules to determine whether the install can go ahead, eg are the requisite files in place?

- Record configuration

Gets the configuration and places it in the container in case it's useful later. Passwords are obfuscated with a repeated SHA-1 hash.

- Remove modules configured for removal

If you start with a full build image and want to test the rebuild of a module, then you can configure modules for removal as part of the build and they will be removed before being built.

- Build modules

Builds the module given the commands that are programmed.

At the end of each module, each module can be configured to tag, export, save, or push the resulting container.

- Test modules

Modules are tested using the test hooks for each module.

- Finalize modules

There's a final cleanup function that's run on each module before the end

- Finalize container

The container is finalized by the core setup module. As part of this it will tag, export, save, or push the resulting image depending on configuration.



#### Module hook functions

These all return True if OK (or the answer is "yes" for is\_installed), or False if not OK (or the answer is "no" for is\_installed).

If False is returned for all functions (except is\_installed), the build will fail.

- is\_installed

Used by "Check ready" part of lifecycle to determine whether the module is installed or not.

- remove

Handles the removal of the module. Useful for quick test of a recently-changed module.

- build

Handles the building of the module

- start

Handles the starting of the module. When tests are run all modules that have been built or are installed are started up.

- stop

Handles the stopping of the module. When any kind of persistence is performed, all modules that have been built or are installed are stopped first, then started again once done.

- test

Handles the testing of the module.

- get\_config

Gathers configuration for the module.


#### Module dependencies

Module conflicts

	


	
## Invocation

General help:

```
$ shutit -h
usage: shutit [-h] {build,sc,serve,skeleton} ...

ShutIt - a tool for managing complex Docker deployments. To view help for a
specific subcommand, type ./shutit <subcommand> -h

positional arguments:
  {build,sc,serve,skeleton}
                        Action to perform. Defaults to 'build'.

optional arguments:
  -h, --help            show this help message and exit
```


Build module:

```
$ shutit build -h
usage: shutit build [-h] [--export] [--save] [--push] [--config CONFIG]
                    [-s SEC KEY VAL] [--image_tag IMAGE_TAG]
                    [-m SHUTIT_MODULE_PATH] [--pause PAUSE] [--debug]
                    [--interactive INTERACTIVE] [--ignorestop] [--ignoreimage]

optional arguments:
  -h, --help            show this help message and exit
  --export              export to a tar file
  --save                save to a tar file
  --push                push to a repo
  --config CONFIG       Config file for setup config. Must be with perms 0600.
                        Multiple arguments allowed; config files considered in
                        order.
  -s SEC KEY VAL, --set SEC KEY VAL
                        Override a config item, e.g. "-s container rm no". Can
                        be specified multiple times.
  --image_tag IMAGE_TAG
                        Build container using specified image - if there is a
                        symbolic reference, please use that, eg
                        localhost.localdomain:5000/myref
  -m SHUTIT_MODULE_PATH, --shutit_module_path SHUTIT_MODULE_PATH
                        List of shutit module paths, separated by colons.
                        ShutIt registers modules by running all .py files in
                        these directories.
  --pause PAUSE         Pause between commands to avoid race conditions.
  --debug               Show debug.
  --interactive INTERACTIVE
                        Level of interactive. 0 = none, 1 = honour pause
                        points and config prompting, 2 = query user on each
                        module, 3 = tutorial mode
  --ignorestop          ignore STOP* files
  --ignoreimage         ignore disallowed images
```

Create new skeleton module:

```
$ shutit skeleton -h
usage: shutit skeleton [-h] [--example] [-d DOCKERFILE]
                       module_directory module_name domain [script]

positional arguments:
  module_directory      absolute path to new directory for module
  module_name           name for your module
  domain                arbitrary but unique domain for namespacing your
                        module, eg com.mycorp
  script                pre-existing shell script to integrate into module
                        (optional)

optional arguments:
  -h, --help            show this help message and exit
  --example             add an example implementation with model calls to
                        ShutIt API
  -d DOCKERFILE, --dockerfile DOCKERFILE

```

Show computed configuration:

```
$ shutit sc -h
usage: shutit sc [-h] [--history] [--config CONFIG] [-s SEC KEY VAL]
                  [--image_tag IMAGE_TAG] [-m SHUTIT_MODULE_PATH]
                  [--pause PAUSE] [--debug] [--interactive INTERACTIVE]
                  [--ignorestop]
 optional arguments:
   -h, --help            show this help message and exit
   --history             show config history
   --config CONFIG       Config file for setup config. Must be with perms 0600.
                         Multiple arguments allowed; config files considered in
                         order.
   -s SEC KEY VAL, --set SEC KEY VAL
                         Override a config item, e.g. "-s container rm no". Can
                         be specified multiple times.
   --image_tag IMAGE_TAG
                         Build container using specified image - if there is a
                         symbolic reference, please use that, eg
                         localhost.localdomain:5000/myref
   -m SHUTIT_MODULE_PATH, --shutit_module_path SHUTIT_MODULE_PATH
                         List of shutit module paths, separated by colons.
                         ShutIt registers modules by running all .py files in
                         these directories.
   --pause PAUSE         Pause between commands to avoid race conditions.
   --debug               Show debug.
   --interactive INTERACTIVE
                         Level of interactive. 0 = none, 1 = honour pause
                         points and config prompting, 2 = query user on each
                         module, 3 = tutorial mode
   --ignorestop          ignore STOP* files
```



## ShutIt API

### Introduction

The shutit object represents a build with an associated config. In theory multiple builds could be represented within one run, but this is functionality yet to be implemented. 

Calling methods on the object effect and affect the build in various ways and help manage the build process for you.

Help on methods on the shutit object (defined in shutit_global.py):

```
       add_line_to_file(self, line, filename, expect=None, child=None, match_regexp=None, truncate=False, force=False, literal=False)
           Adds line to file if it doesn't exist (unless Force is set).
           Creates the file if it doesn't exist (unless truncate is set).
           Must be exactly the line passed in to match.
           Returns True if line added, False if not.
           If you have a lot of non-unique lines to add, it's a good idea to have a sentinel value to
           add first, and then if that returns true, force the remainder.
           
           - line         - Line to add.
           - filename     - Filename to add it to.
           - match_regexp - If supplied, a regexp to look for in the file instead of the line itself, handy if the line has awkward characters in it.
           - truncate     - Truncate or create the file before doing anything else
           - force        - Always write the line to the file
           - literal      - If true, then simply grep for the exact string without bash interpretation
       
       add_to_bashrc(self, line, expect=None, child=None)
           Takes care of adding a line to everyone's bashrc.
       
       do_repository_work(self, repo_name, expect=None, docker_executable='docker', password=None, force=None)
           Commit, tag, push, tar the container based on the configuration we have.
       
       fail(self, msg, child=None)
           Handles a failure, pausing if a pexpect child object is passed in.
       
       file_exists(self, filename, expect=None, child=None, directory=False)
           Return True if file exists, else False
       
       get_config(self, module_id, option, default, boolean=False)
           # Pass-through function for convenience
       
       get_default_check_exit(self)
           Returns default value of check_exit. See send method.
       
       get_default_child(self)
           Returns the currently-set default pexpect child.
       
       get_default_expect(self)
           Returns the currently-set default pexpect string (usually a prompt).
       
       get_distro_info(self, child=None)
           Get information about which distro we are using.
           
           Fails if distro could not be determined.
           Should be called with the container is started up, and uses as core info as possible.
       
       get_file_perms(self, filename, expect=None, child=None)
           Returns the file permission as an octal string.
       
       get_output(self, child=None)
           Helper function to get latest output.
       
       get_re_from_child(self, string, regexp)
           Get regular expression from the first of the lines passed in in string that matched.
           Returns None if none of the lines matched.
       
       install(self, package, child=None, expect=None, options=None, timeout=3600)
           Distro-independent install function.
           Takes a package name and runs the relevant install function.
           Returns true if all ok (ie it's installed), else false
       
       is_user_id_available(self, user_id, child=None, expect=None)
           Determine whether a user_id for a user is available.
       
       log(self, msg, code=None, pause=0, prefix=True, force_stdout=False)
           Logging function.
           
           code         - Colour code for logging. Ignored if we are in serve mode.
           pause        - Length of time to pause after logging (default: 0)
           prefix       - Whether to output logging prefix (LOG: <time>) (default: True)
           force_stdout - If we are not in debug, put this in stdout anyway (default: False)

       login(self, user='root', command='su -', child=None, password=None)
           Logs the user in with the passed-in password and command.
           Tracks the login. If used, used logout to log out again.
           Assumes you are root when logging in, so no password required.
           If not, override the default command for multi-level logins.
           If passwords are required, see setup_prompt() and revert_prompt()
           
           user     - User to login with
           command  - Command to login with
           child    - See send()
       
       logout(self, child=None)
           Logs the user out. Assumes that login has been called.
           If login has never been called, throw an error.
           
           - child              - See send()
       
       ls(self, directory)
           Helper proc to list files in a directory
           
           Returns list of files.
           
           directory - directory to list

       mount_tmp(self)
           mount a temporary file system as a workaround for the AUFS /tmp issues
           not necessary if running devicemapper
       
       module_method_end(self)
           Gets called automatically by the metaclass decorator in
           shutit_module when a module method is finished.
           This allows setting defaults for the 'scope' of a method.
       
       module_method_start(self)
           Gets called automatically by the metaclass decorator in
           shutit_module when a module method is called.
           This allows setting defaults for the 'scope' of a method.
       
       package_installed(self, package, expect=None, child=None)
           Returns True if we can be sure the package is installed.
       
       pause_point(self, msg, child=None, print_input=True, expect='', level=1)
           Inserts a pause in the build session which allows the user to try things out before continuing.
       
       prompt_cfg(self, msg, sec, name, ispass=False)
           Prompt for a config value, possibly saving it to the user-level cfg
       
       push_repository(self, repository, docker_executable='docker', child=None, expect=None)
           Pushes the repository.
           
           - repository        - 
           - docker_executable -
       
       record_config(self)
           # Put the config in a file in the container.
       
       remove(self, package, child=None, expect=None, options=None, timeout=3600)
           Distro-independent remove function.
           Takes a package name and runs relevant remove function.
           Returns true if all ok (ie it's installed now), else false
       
       revert_prompt(self, old_prompt_name, new_expect=None, child=None)
           Reverts the prompt to the previous value (passed-in).
           
           It should be fairly rare to need this. Most of the time you would just
           exit a subshell rather than resetting the prompt.
       
       run_script(self, script, expect=None, child=None, in_shell=True)
           Run the passed-in string on the container's command line.
           
           - script   - 
           - expect   - 
           - child    - 
           - in_shell -
       
       send = send_and_expect(self, send, expect=None, child=None, timeout=3600, check_exit=None, fail_on_empty_before=True, record_command=None, exit_values=None, echo=None)
       
       send_and_expect(self, send, expect=None, child=None, timeout=3600, check_exit=None, fail_on_empty_before=True, record_command=None, exit_values=None, echo=None)
           Send string to the container prompt, and wait until the expected string is seen before returning.
           The expected string will default to the currently-set default expected string (see get_default_expect)
           
           Returns the pexpect return value (ie which expected string in the list matched):
           
           child                      - pexpect child to issue command to.
           send                       - String to send, ie the command being issued.
           expect                     - String that we expect to see in the output. Usually a prompt.
                                        Defaults to currently-set expect string (see set_default_expect)
           timeout                    - Timeout on response (default=3600 seconds).
           check_exit                 - Whether to check the shell exit code of the passed-in command.
                                        If the exit value was non-zero an error is thrown.
                                        (default=None, which takes the currently-configured check_exit value)
                                        See also fail_on_empty_before.
           fail_on_empty_before       - If debug is set, fail on empty match output string (default=True)
                                        If this is set to False, then we don't check the exit value of the 
                                        command.
           record_command             - Whether to record the command for output at end (default=True)
                                        As a safety measure, if the command matches any 'password's then we 
                                        don't record it.
           exit_values                - Array of acceptable exit values (default [0])
       
       send_and_get_output(self, send, expect=None, child=None)
           Returns the output of a command run.
       
       send_file(self, path, contents, expect=None, child=None, log=True)
           Sends the passed-in string as a file to the passed-in path on the container.
           
           - path     - Target location of file in container.
           - contents - Contents of file as a string. See log.
           - expect   - 
           - child    - 
           - log      - Log the file contents if in debug.
       
       send_host_dir(self, path, hostfilepath, expect=None, child=None, log=True)
           Send file from host machine to given path
           - path         - path to send file to
           - hostfilepath - path to file from host to send to container
           - expect       - arg to pass to send_file (default None)
           - child        - arg to pass to send_file (default None)
           - log          - arg to pass to send_file (default True)
       
       send_host_file(self, path, hostfilepath, expect=None, child=None, log=True)
           Send file from host machine to given path
           - path         - path to send file to
           - hostfilepath - path to file from host to send to container
           - expect       - arg to pass to send_file (default None)
           - child        - arg to pass to send_file (default None)
           - log          - arg to pass to send_file (default True)
       
       set_default_child(self, child)
           Sets the default pexpect child.
       
       set_default_expect(self, expect=None, check_exit=True)
           Sets the default pexpect string (usually a prompt).
           Defaults to the configured root_prompt.
       
       set_password(self, password, user='', child=None, expect=None)
           Sets the password for the current user or passed-in user.
       
       setup_prompt(self, prompt_name, prefix='TMP', child=None, set_default_expect=True)
           Use this when you've opened a new shell to set the PS1 to something sane.
       
       user_exists(self, user, expect=None, child=None)
           Returns true if the specified username exists
       
       ----------------------------------------------------------------------
       Data descriptors defined here:
       
       __dict__
           dictionary for instance variables (if defined)
       
       __weakref__
           list of weak references to the object (if defined)

FUNCTIONS
    init()
        Initialize the shutit object. Called when imported.
    
    random_id(size=5, chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        Generates a random string of given size from the given chars.

DATA
    cfg = {'action': {}, 'build': {'build_id': 'lp01728_imiell_1405067894....
    cwd = '/space/git/shutit'
    pexpect_children = {}
    shutit = <shutit_global.ShutIt object>
    shutit_command_history = []
    shutit_main_dir = '/space/git/shutit'
    shutit_map = {}
    shutit_modules = set([])
```

### Configuration

Configuration is specified in .cnf files.

These are divided up into sections:

#### Sections

##### container

Config pertaining to the container.

Defaults from util.tcl:

```
# Details relating to the container you are building itself
[container]
# Root password for the container - replace with your chosen password
# If left blank, you will be prompted for a password
password:YOUR_CONTAINER_PASSWORD
# Hostname for the container - replace with your chosen container name
hostname:
force_repo_work:no
locale:en_US.UTF-8
# space separated list of ports to expose
# e.g. "ports:2222:22 8080:80" would expose container ports 22 and 80 as the
# host's 2222 and 8080
ports:
# Name to give the container. Empty means "let docker default a name".
name:
# Whether to remove the container when finished.
rm:no
```

##### host

Config pertaining to the container.

```
# Information specific to the host on which the build runs.
[host]
# Folder with files you want to copy from in your build.
# Often a good idea to have a central folder for this per host
# in your /path/to/shutit/configs/`hostname`_`username`.cnf
# If set to blank, then defaults to /path/to/shutit/artifacts (preferred)
# If set to "artifacts", then defaults to the artifacts folder in the cwd.
artifacts_dir:
# Docker executable on your host machine
docker_executable:docker
# space separated list of dns servers to use
dns:
# Password for the username above on the host (only needed if sudo is needed)
password:
# Log file - will be set to 0600 perms, and defaults to /tmp/<YOUR_USERNAME>_shutit_log_<timestamp>
# A timestamp will be added to the end of the filename.
logfile:
```

##### repository

Config pertaining to the persistence of the container, enabling commit, tag, save and push.

Defaults from util.tcl:

```
# Repository information
[repository]
# Whether to tag
tag:no
# Whether to suffix the date to the tag
suffix_date:yes
# Suffix format (default is epoch seconds (%s), but %Y%m%d_%H%M%S is an option if the length is ok with the index)
suffix_format:%s
# tag name
name:my_repository_name
# Whether to tar up the docker image exported
export:no
# Whether to tar up the docker image saved
save:no
# Whether to push to the server
push:no
# User on registry to namespace repo - can be set to blank if not docker.io
user:
#Must be set if push is true/yes and user is not blank
password:YOUR_INDEX_PASSWORD_OR_BLANK
#Must be set if push is true/yes and user is not blank
email:YOUR_INDEX_EMAIL_OR_BLANK
# repository server
# make blank if you want this to be sent to the main docker index on docker.io
server:
# tag suffix, defaults to "latest", eg registry/username/repository:latest.
# empty is also "latest"
tag_name:latest
```

##### build

Config pertaining to the build process.

Defaults from util.tcl:

```
# Aspects of build process
[build]
build_log:no
# Run container in privileged mode
privileged:no
# lxc-conf arg, eg
#lxc_conf:lxc.aa_profile=unconfined
lxc_conf:
# Base image can be over-ridden by --image_tag defaults to this.
base_image:ubuntu:14.04
# Whether to perform tests. 
dotest:yes
# --net argument, eg "bridge", "none", "container:<name|id>" or "host". Empty means use default (bridge).
net:
```

##### shutit.tk.setup

Config pertaining to the base setup of the container before any modules are run.

#### Per-module config

For each module, extra configs are created by default. These are:

- tagmodule

Whether to tag the module at the end of its build. Useful for debugging to return to a certain point if necessary.

The format of the tag is "module id"\_"module run order"

- build

Whether to build this module. 

Dependency management will auto-set this for you, but you may want to ensure a module always gets built (eg a debugging tool not directly related to your application).

- remove

Whether to invoke the remove function within the module before the build starts.

You can set these eg:

```
[com.mycorp.mymodule.modulename]
# Whether to tag the module at the end of its build.
shutit.core.module.tag:no
# eg to add in a module that 
shutit.core.module.build:no
# Whether to remove the module before building (if is\_installed returns true)
shutit.core.module.remove:no
```

[Github]: https://github.com/ianmiell/shutit


Directory Structure
--------
Each module directory should contain modules that are grouped together somehow
and all/most often built as an atomic unit.
This grouping is left to the user to decide, but generally speaking a module
will have one relatively simple .py file.

Each module .py file should represent a single unit of build. Again, this unit's
scope is for the user to decide, but it's best that each module doesn't get too
large.

Within each module directory the following directories are placed as part of
`./shutit skeleton`.

- test
    - should contain ```test_`hostname`.sh``` executables which exit with a 
            code of 0 if all is ok.
- configs
    - default configuration files are placed here.
- context
    - equivalent to dockerfile context

These config files are also created, defaulted, and automatically sourced:

```
configs/build.cnf                  - 
```

And these files are also automatically created:

```
configs/README.md                  - README for filling out if required
run.sh                             - Script to run modules built with build.sh
build.sh                           - Script to build the module
```

Configuration
--------
See config files (in configs dirs) for guidance on setting config.

Tests
--------
Run 

```
cd test && ./test.sh
```

Known Issues
--------------
Since a core technology used in this application is pexpect - and a typical
usage pattern is to expect the prompt to return. Unusual shell
prompts and escape sequences have been known to cause problems.
Use the ```shutit.setup_prompt()``` function to help manage this by setting up
a more sane prompt.
Use of ```COMMAND_PROMPT``` with ```echo -ne``` has been seen to cause problems
with overwriting of shells and pexpect patterns.


Licence
------------
The MIT License (MIT)

Copyright (C) 2014 OpenBet Limited

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

