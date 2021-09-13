This document lists the steps needed to execute jobs on NTU HPC. Except for the Pulse Secure VPN (which is specific to NTU), all the other parts apply to any HPC system which uses PBS Job Scheduler. To connect to NTU HPC, we need to configure VPN first. Therefore, we shall learn about the following:
	
  * [VPN Installation and Usage](#vpn-installation-and-usage)
* [Accessing the Remote (HPC) Server](#accessing-the-remote-hpc-server)
* [Introduction to HPC](#introduction-to-hpc)
* [Job Submission](#job-submission)
* [Checking Balance and Job Details](#checking-balance-and-job-details)
* [Space Enquiry](#space-enquiry)

### VPN Installation and Usage
* For Windows and MacOS, follow the [NTU VPN guide](https://www3.ntu.edu.sg/cits2/ras/for_cms_ref/QuickStartGuideVPN.pdf) to setup and connect to the VPN.
* For Linux (specifically Ubuntu), there are two options:
	* **1. Installing Pulse Secure Client on Linux**

	  Follow the steps mentioned [here](https://gist.github.com/eugenetriguba/beb90e0bca7e5299436693d9b74a9853) to setup Pulse Secure on Linux. After this, you will be able to start it by executing `vpn` on the terminal. When connecting for the very first time, you will need to add a new connection:
		* Enter a connection name as per your choice (say `NTU VPN`) and the URL as `https://ntuvpn.ntu.edu.sg`
		* Hit **Connect**. Enter the username and password when prompted.
		
      **Tip:** _To kill the Pulse Secure Client's process, you need to execute `/usr/local/pulse/pulsesvc -K`. `kill -9` and `pkill` do not work in this case._
	* **2. Using OpenConnect (Recommended)**
		* Install OpenConnect by following the steps mentioned [here](https://people.eng.unimelb.edu.au/lucasjb/archive/oc_old.html).
		* Open Network Manager in Linux: _Settings --> Network_. Click the "+" sign beside "VPN". Select "Multi-protocol VPN client (openconnect)".
		* Go to the "Identity" tab. Select "Pulse Connect Secure" in the VPN Protocol field.
		* Put `ntuvpn.ntu.edu.sg` in the "Gateway" field.
		* Download the CA certificate (Go to `ntuvpn.ntu.edu.sg` website. Click the lock icon in the address bar and click the Export button).
		* Rename this downloaded certificate as `<something>.crt`
		* Link this in the "CA Certificate" field.
		* Click "Apply" on the top right.

		Now you should be able to connect to NTU VPN by turning on the VPN from the dropdown menu on the top right in Linux (where Wi-Fi, Volume, etc settings are mentioned), and providing username and password. This offers a smoother experience compared to Pulse Secure Client.

Now that we have installed the VPN, we need an SSH client to access the remote machine.

### Accessing the Remote (HPC) Server
  * **Windows**:
    MobaXterm is a great SSH client with a dedicated SFTP bar that lets you browse files on the remote machine conveniently. Download it from [here](https://mobaxterm.mobatek.net/download.html) and install the same.

  * **Linux**:
    * _Wine + MobaXterm_
        
        I recommend using this setup. This is the best setup I found for Linux since MobaXterm provides a sidebar for file access.
        * Install latest version of wine from [here](https://wiki.winehq.org/Ubuntu).
        * Download MobaXterm executable (i.e. the Portable edition) from [here](https://mobaxterm.mobatek.net/download-home-edition.html).
        * Run the executable to use MobaXterm: `nohup wine /path/to/MobaXterm/exe &`. _The `nohup` and `&` facilitate the execution of the MobaXterm application in the background. So, even if you close the terminal, it continues to run._
    * _Linux Terminal + File Manager_
        * Open the Linux terminal and enter `ssh -X <username>@gekko.hpc.ntu.edu.sg`
        * Enter your password when prompted. This gets you on the login node of Gekko cluster.
        * Accessing the files using the terminal is tedious. To ease the process, use the File Manager to mount the remote server using SFTP:
          * Open the Linux File Manager. 
          * Go to "Other Locations" in the left pane.
          * On the bottom of the screen, enter `sftp://<username>@gekko.hpc.ntu.edu.sg/` in the `Connect to Server` field.
          * Hit "Connect" and enter the password when prompted.
          
          **Tip**: _On Ubuntu, you can use Ctrl + L to turn the path bar into a text field. This is really hepful while copying and pasting paths. Use Ctrl + R to refresh the current view. This is helpful since if you delete or add a file from an alternate SFTP connection, it doesn't reflect in File Manager automatically and a refresh is required._

  * **MacOS**:
    Just like linux, either [use the Mac terminal](https://www.ssh.com/academy/ssh/putty/mac#using-the-built-in-ssh-client-in-mac-os-x), or use [PuTTY](https://www.ssh.com/academy/ssh/putty/mac#ported-putty-for-mac)/[Cyberduck](https://cyberduck.io/).

Once you have downloaded and configured the SSH client you choose to use, you can proceed to actually using the HPC.


### Introduction to HPC
Being a shared resource, installation of applications is maintained uniquely at HPC. Everything is installed centrally as *modules*, which users can load when needed. Once you load a *module*, it works the same way as if it were installed on your system.

#### Working with modules
  * See the available modules: `module avail`
  * Load a module: `module load <modulename>`
  * See the loaded modules: `module list`
  * Unload a module: `module unload <modulename>`
  * Unload all loaded modules: `module purge`

#### Using conda environments	
  * Conda envs work the same way on Gekko as they do locally.
  * First, load the anaconda module:
    ```
    module load anaconda2020/python3
    ```
  * Now, execute the following to enter the `base` conda environment (Gekko will also prompt you to do so):
    ```
    eval "$(/usr/local/anaconda3-2020/bin/conda shell.bash hook)"
    ```
  * Now you can use the existing environments or create your own. Follow [this guide](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) for all things conda envs.


#### HPC terminology
**Jobs**: To execute resource intensive programs on HPC, we submit them as jobs that get scheduled. A job is therefore just a sequence of commands which is set for execution.

**Queues**:  Once we submit a job, it gets queued for execution. There are various queues depending on the resources (in terms of CPU/GPU) they offer. The details about different queues available on NTU HPC system can be seen [here (requires NTU account for access)](https://entuedu.sharepoint.com/teams/ntuhpcusersgroup2/SitePages/Queue-Information-and-Pricing.aspx).

**Walltime**: The amount of time requested for a job is called the walltime. This may be larger than the actual runtime of your job. This is used to schedule your job. So, enter a value larger than the actual runtime.

**Scratch**: It is a storage space at `scratch/<username>` which can be used for fast input/output. It uses high performant SSDs and therefore, reads and writes to this location are faster compared to `/home/<username>`. For data intensive applications, consider using `scratch` space to store the data.

#### Queues
* The command we use to know about the status of jobs on queues is `qstat`.
* To know the different queues with their maximum allowed walltime: `qstat -q`
* To know the status of your jobs on HPC: `qstat -u <username>`

### Job Submission
Let's now see how a job script written for PBS Scheduler looks like. Job templates for various use-cases are already available for use. You can find them at `/usr/local/templates/` on Gekko. Below is a line by line explanation of the job script template that I used (available as [`job_script.pbs`](https://github.com/mdrpanwar/SpeakerDiarization/blob/main/HPC_Guide/job_script.pbs) file in the current directory as well).

<p align="center">
  <img src='../img/pbs_script.png'/>
</p></center>

* Once you have written a job script, you can submit it using `qsub <job_script.pbs>`. It will output a `JOB ID`. The job will now get queued or start executing. You can check its status using `qstat -u <username>` as mentioned above. It will show all of your jobs with their `JOB ID`s and execution statuses (Queued (Q) or Running (R)).
 
* To delete a job, execute `qdel <JOB_ID>`. You will be charged for the walltime the job has used until the point of deletion.

* For details, please refer the [Gekko User Guide (requires NTU account for access)](https://entuedu.sharepoint.com/teams/ntuhpcusersgroup2/SitePages/Quick-User-Guide-on-Gekko.aspx).

* If you have any questions, please go through the discussions on [NTU HPC forum (requires NTU account for access)](https://www.yammer.com/e.ntu.edu.sg/#/threads/inGroup?type=in_group&feedId=15849979904&view=all) and post a query if needed.

### Checking Balance and Job Details
If you use paid queues, your project account (`PROJECT_CODE` in [`job_script.pbs`](https://github.com/mdrpanwar/SpeakerDiarization/blob/main/HPC_Guide/job_script.pbs)) will be charged accordingly. To check your balance, follow the steps mentioned below.

* Login as an account manager:
```
amgr login
// Enter your password
```
* Checking account balance (both commands serve the same purpose):
	* `amgr report project -n <PROJECT_CODE> -h`
	* `amgr checkbalance project -n <PROJECT_CODE>`

* Check the detailed transaction report for a job:
```
amgr report transaction -i <JOB_ID> -l 
```

### Space Enquiry
To know the space consumption of your data on the HPC, you can use `du` and `df` utilities but they are slow. A faster implementation is provided by the NTU HPC team and it can be used as follows.
* See usage for `home` and `scratch` directories:
```
gekko space home scratch
```
* See usage for a specific path:
```
gekko space -p /path/whose/space/needs/to/be/checked
```
* There are many `gekko` utilities, a list of all can be seen by:
```
gekko --help
```
