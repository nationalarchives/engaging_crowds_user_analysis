# Getting Started

These instructions assume that you are working with a pseudionymized classifications file downloaded from the Engaging Crowds' [data sharing platform](https://tanc-ahrc.github.io/EngagingCrowds/Data).

## Set Up Environment

Clone this project
```
 git clone https://github.com/nationalarchives/engagingcrowds_engagement.git
```

Install the dependencies. It is often a good idea to do this inside a virtualenv.
```
mkvirtualenv ec_engagement
pip install pandas
```

> :warning: The original requirements.txt used to generate data for the report was
lost during development. The requirements.txt provided here ought to
generate the same results.

Create the `secrets/` directory.
```
mkdir engagingcrowds_engagement/secrets
chmod 700 secrets #if required by your privacy policies
```

## Prepare Pseudonymized Data

You can either use pre-pseudonymised data from the Engaging Crowds project or classifications from your own Zooniverse project.

### Use Pre-Pseudonymised Data

* Download the data from the [Engagement Analysis](https://tanc-ahrc.github.io/EngagingCrowds/Engagement%20Analysis%20Data.html) page of the data sharing platform.
* Unpack the zip or tarball that you have downloaded
  * `unzip data_analysis.zip`
  * `tar xf data_analysis.tar.xz`
* `cp data_analysis/all_classifications.csv engagingcrowds_engagement`

### Use Your Own Classifications

Create a directory to store your exports:
```
mkdir engagingcrowds_engagement/exports
chmod 700 engagingcrowds_engagement/exports #if required by your privacy policies
```

Download the classifications from your Zooniverse project(s). At time of writing, this requires:
* Go to the Project Builder
* Select your project
* Go to `Data Exports`
* Press `Request new workflow classification export`
* Select the appropriate workflow and download to `engagingcrowds_engagement/exports`
* Repeat for as many workflows/projects as you need

Run the pseudonymizer
```
cd engagingcrowds_engagement
./pseudonymize.py
```
> :warning: There are assumptions relating to Engaging Crowds in the scripts. You will likely need to change them to work with your project. This should really be engineered so that the script can be easily configured for different projects: patches welcome.

This creates:
* `all_classifications.csv`: Pseudonymised classifications from all workflows, suitable to input to `analyze.py`
* `secrets/*-classifications.csv`: More lightly altered pseudonymized classifications, with one file per workflow. These should be more suitable for analysis with scripts published by Zooniverse.
* `secrets/identities.json`: Dictionary mapping user ids to pseudonyms
* `sharing/*.{zip,tar.xz}`: Pseudonymised data packaged for the data sharing platform
* `README_all_classifications`: A README for the data sharing platform. This can be packaged by `share_analysis.py`.

### About the `all_classifications.csv` file
In the raw data, logged-in users are identified by their user id. Other users are identified by a hash of their IP address. This hash will not necessarily always identify the same individual.

Either kind of identifier will always be pseudonymised to the same value within a single run of `pseudonymize.py`. Logged-in users receive a pseudonym prefixed with `name:` and other users recieve a pseudonym prefixed with `anon:`.

If an `identities.json` from a previous run is available then the same pseudonym will continue to be used for a given identifier. This allows us to observe the behaviour of (non-identifiable) individuals across all workflows and projects.

We are quite conservative in what we consider to be "personal" data. Any data with any whiff of the personal about it is left out of `all_classifications.csv`.

See the downloads on the [data sharing platform](https://tanc-ahrc.github.io/EngagingCrowds/Data.html) for examples of pseudonymised classification files and explanatory readmes.
The files for the data sharing platform contain pseudonymised classifications for each project and an explanatory README file.

# Analysing Data

Just run the analysis script.
```
cd engagingcrowds_engagement
./analyze.py
```

:warning: There are assumptions relating to Engaging Crowds in the scripts. You may need to change them to work with your project. Patches to make the scripts more generic are welcome.

This script analyzes data created by logged-in users. It creates the following files under `` secrets/graphs/`git rev-parse HEAD` ``:
* `log.txt` Everything written to stdout as the script runs. This includes information about discarded classifications, a breakdown of volunteers by project contributed to, brief statistical overviews of workflow durations.
* `prepared_classifications.csv` A dump of `all_classifications.csv` as transformed for this analysis. It has some additional computed fields. It also has discarded classifications which are to be left out of the analysis.
* `class_counts/{project,workflow,workflow_type}/{dynamic,static}/*_vol.{png,svg,html}` Charts showing percentage of classifications by buckets of volunteers, sorted by number of contributions.
* `class_times/{project,workflow,workflow_type}/all_classifiers/{dynamic,static}/*.{png,svg,html}` Various visualisations relating mainly to when classifications happened within a project, workflow or workflow type.
  * Box plots of number of classifications made per volunteer (`*_box.*`)
  * Heat maps of density of classifications at time of day and day of week (no "`_` suffix" in the file name)
  * The same heat map for a random 25% of the data. We generate 4 of these with names like `HMS_NHS_r1.html`, `HMS_NHS_r2.html`, `HMS_NHS_r3.html`, `HMS_NHS_r4.html`.
  * The same heat map for volunteers in the lower quartile of classifications made (`*_q1.*`)
  * The same heat map for volunteers in the lower 3 quartiles of classifications made (`*_q3.*`)
  * The same heat map for volunteers in the top quartile of classifications made (`*_q4.*`)
  * Heatmaps from random samples of the data of the same quantity as the similarly-named 'quartile' heatmap. There are 4 such charts for each of the above 'quartile-based' heat maps, named like `*_q*_r1.*`, `*_q*_r2.*`, `*_q*_r3.*` and `*_q*_r4.*`.
  * Heatmaps from random samples of one quarter of the full data set. For example, `HMS_NHS_r1.html` is based on a random sample from the full data set of one quarter of the classifications. As before, there are 4 such charts, named like `*_r1.*`, `*_r2.*` `*_r3.*` and `*_r4.*`.
* `class_times/{project,workflow,workflow_type}/first_last_day/{dynamic,static}/*.{png,svg,html}` Visualisations relating to when volunteers first and last classified on a project, workflow or workflow type.
  * Bar chart of number of volunteers first classifying on date (`*_firstday.*`)
  * Bar chart of number of volunteers last classifying on data (`*_lastday.*`)
  * Combined bar chart and line chart, with bars showing gain in volunteers on each date and line showing total 'active' volunteers on each day (volunteers who have made their first classification but not yet made their last classification) (`*_gain.*`)
  * For projects and workflow types only, a line chart of 'active' volunteers on each data, broken down by workflow (`*_agg_gain.*`). For HMS NHS the chart is very cluttered and so we draw a scatter plot instead. HMS NHS also has a couple of alternative versions of this chart:
    * `HMS_NHS_agg_gain_letters.*`: A scatter plot using letters in place of symbols.
    * `HMS_NHS_agg_gain_line.*`: A line chart with thicker lines and no symbols
* `class_times/workflow/duration_stats/{dynamic,static}/all_times_box.{png,svg,html}` A box plot of time taken for each classification. This chart is entirely dominated by outliers.
* `class_times/{project,workflow,workflow_type}/{all_classifiers,first_last_day,duration_stats}/*.csv` Dumps of the data visualised in the respective charts.

Throughout:
* Charts and data are within the scope of project, workflow and workflow type under the respective directories.
* Lightly interactive HTML charts are in the `dynamic` directory.
* Non-interactive `.png` and/or `.svg` charts are in the `static` directory.
* The data visualised by the charts is in corresponding CSV files one level above the `dynamic` and `static` directories.

There may be bugs in the code that generates these graphs, especially for graphs that were not used in the Engaging Crowds project report.

# Sharing Data

The data sharing code is just for creating deliverables for the Engaging Crowds [data sharing platform](https://tanc-ahrc.github.io/EngagingCrowds/Data). At time of writing, the pseudonymisation step places most of this data in `engagingcrowds_engagement/sharing/`. The data used as input to the analysis step can be added by running `./share_analysis.py`.[^1]

[^1]: At one time, outputs from `analyze.py` were included in the bundle for the data sharing platform. This is no longer the case and so the functionality in `share_analysis.py` could just be merged into `pseudonymise.py`.

The integrity of the bundles can be checked with `./test_shareables/test_shareables.sh`.

Data can be copied to the data sharing platform by running `./to_site.sh`. This should be given a path to the location of a clone of the data sharing platform, for example `./to_site.sh ../simple-site`.

# Libraries

Several of the Python files are libaries used by other scripts.

* `analyze_class.py` Used to produce charts showing classifications by buckets of volunteers, sorted by number of contributions. These show the expected power law distribution of volunteer contributions: a small number of volunteers contribute a large number of classifications.
* `analyze_startstop.py` Used to produce charts relating to the first and last date on which each volunteer made a classification.
* `analyze_time.py` Used to produce charts relating to the time of day when classifications are made (and box plots relating to number of classifications made per volunteer)
* `contributors.py` Used to produce information about the number of Engaging Crowds projects contibuted to by each volunteer.
* `data.py` Provides information about the projects, workflows and classifications of Engaging Crowds. Serves as a config file of sorts.
* `util.py` A few utility functions to be used by other scripts: simple filename manipulations, git lookups and a function to log stdout.

# Misc Other Scripts

`analyze.py`, `pseudonymize.py`, `share_analysis.py`, `to_site.sh` and associated libraries are described above. A few other scripts sit in this repository. They were used for various ad hoc purposes during development and may or may not still work. The following descriptions are to the best of my memory.

* `check_csv_dumps.sh` Compares CSV files dumped by the analysis script in latest commit vs a particular previous run. Would have been used to check that changes had only the desired effect.
* `cmp_svg.sh` Assists with comparing SVG files dumped as charts by the analysis scripts. Unlike many image formats, SVG can be reasonably compared with text-comparison techniques. This would have been used to check that changes had only the desired effect.
* `exploration.ipynb` A Jupyter Notebook used for early exploration of the data.
* `jsondump.py` Dumps the names of all JSON key-value pairs in the JSON-formatted fields in the raw classification data. Used to find fields of interest for analysis, and to scan for potential personal data.
* `show_graphs.sh` Opens groups of related graphs in Chrome tabs. More fine-grained than some of the other `show_*.sh` scripts.
* `show_projects.sh` Opens graphs for each Engaging Crowds project in Chrome tabs.
* `show_types.sh` Opens graphs for each of the HMS NHS workflow types in Chrome tabs.
* `show_workflows.sh` Opens graphs for each Engaging Crowds workflow in Chrome tabs.
* `times.ipynb` A Jupyter Notebook used for early exploration of the data.
* `us.sh` Script for identifying classifications by particular users. Used to find classifications made by members of the Engaging Crowds project team.
* `zooniscript.sh` A driver for existing analysis scripts published by Zooniverse.

# Potential Future Work

Features specific to Engaging Crowds could be removed or factored out to be contolled by command-line switches or configuration files. This would make the scripts more immediately usable for other Zooniverse projects.

It would make sense to divide the functions of the scripts out more logically. For example, at present files for the data sharing platform are generated by the same scripts that do the analysis work.

Testing could be much improved.

A general refactoring/tidy-up would be helpful -- in particular there are some rushed late changes that produced some needed outputs but do not make for great code (e.g. the code in `analyze_startstop.py` that uses the `actives` dictionary to generate the "active volunteer" charts).

# Copyright and License

These scripts are Crown Copyright and licensed under the MIT License.
