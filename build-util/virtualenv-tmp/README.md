# virtualenv-tmp #

This folder is used to store virtualenv distributions.
Most files here will be ignored via the `.gitignore` file.
In the following, `VERSION` is the software version (e.g., `1.0.0`) from the
`geoprocessor/app/version.py` file.

Copies of the `geoprocessor` repository working files are copied to the following folders.

## Cygwin ###

Create a virtualenv folder called `gptest-cygwin-VERSION`.
This is useful to pre-test the gptest environment before deployment to production
Linux environments such as Debian and Ubuntu.

The `gptest-cygwin-VERSION` contents can then be linked to,
for example start menus.
