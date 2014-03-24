testprep
========
This package uses CherryPy and XSLT to present user-provided question banks to the user. It is intended for self-testing, rather than for use in a school environment; test security is of little concern.

Current goals:
from an XML file, render html of test questions that may be saved or transferred.
* Ideally, this will have options to
** include styling and JS inline
** include binary files inline, base64 encoded

these are intended to enable the use of a rendered test on multiple devices, requiring only the browser for basic functionality

- TODO: include "why i missed this question" options
- TODO: add tagging options for questions
- TODO: saved AJAX selection history is terrible, improve
