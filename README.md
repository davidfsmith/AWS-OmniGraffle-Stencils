AWS-OmniGraffle-Stencils
========================

If use OmniGraffle and AWS - these stencils are for you.

Omnigraffle compatible versions of the [AWS simple icons](https://aws.amazon.com/architecture/icons/).

## 19.02.07 Icons
Only the light background icons have been converted.  Last updated using: [AWS-Architecture-Icons_EPS_20190207](https://d1.awsstatic.com/webteam/architecture-icons/AWS-Architecture-Icons_EPS_20190207.2b615daa2f47347ca46e67c56bd35be79cea5bee.zip)

## 18.02.22 Icons
Last updated using: [PNG,+SVG,+EPS_18.02.22.zip](https://s3-us-west-2.amazonaws.com/awswebanddesign/Architecture+Icons/AWS-Arch-Icon-Sets_Feb-18/PNG%2C+SVG%2C+EPS_18.02.22.zip)

# Using the stencils

There are two ways to install stencils into Omnigraffle (thanks to [@voxpelli](https://twitter.com/voxpelli/status/1105536267352264705) for pointing out I don't include instructions on how to use the stencil files.)

## Installing a stencil

1. Double click on the stencil file, it will open in Omnigraffle
2. You can then move the stencil to make it available for future use

## Installing all the stencils

1. Use terminal to open the Omnigraffle stencil directory in Finder (for Omnigraffle 7.x) `open $HOME/Library/Containers/com.omnigroup.OmniGraffle7.MacAppStore/Data/Library/Application\ Support/The\ Omni\ Group/OmniGraffle/Stencils`
2. Create a directory called `AWS` or whatever works for you.
3. Copy the stencil files corresponding to the version of the icons you want to use into the `AWS` folder you just created
4. Open Omnigraffle and create awesome diagrams using the AWS Architecture Icons ;-)

Any problems, ommissions ot suggestions then feel free to either raise an [issue](https://github.com/davidfsmith/AWS-OmniGraffle-Stencils/issues) or better yet, fork the repo, make the change and open a PR.

# Creating stencil files

## Converting Icons

### Installing epstopdf

	brew cask install mactex
	
Then install the Ghostscript package from [MacTex packages](http://www.tug.org/mactex/morepackages.html)

### Steps

* Download the latest AWS icons and unzip into the same directory as `convert.sh`
* run `./convert.sh <unzipped AWS icons directory>`

Time passes, but you should find that you'll have just the converted PDF files left in the AWS icons directory.

* Manually add the PDF files to the stencil files.

Dull but works, drag and dropping the PDF files into a stencil template can be a bit hit and miss.  I've found the best way is to copy and paste in each icon, then group, name and add on the anchor points.

Dull, but handy.

## Todo

Automate the process more, sadly trying to open the .gstencil plist files results in an error and needs more research.  Additional file renaming steps for the converted icons as well as creating a basic URL look up / list of files would help reduce some of the manual steps.