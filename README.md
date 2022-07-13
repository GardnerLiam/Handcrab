# Handcrab

# Version
2.1

# Changelog (V2+)
Version 2 &mdash; Updated default command to work for BCC format. Conversion no longer adds `<h1>...</h1>` to the document. `\section` now produces an `h2` heading.

Version 2.1 &mdash; 
-  Updated documentation. 
- `\section` maps to `h1` now, but this can be changed using the `--heading-level` or `-hl` parameter.
- Resource templates *should* be able to work without `<h1>Title</h1>`, if a static title is desired.
- added `-math-circles-title` or `-mct` parameter for converting math circles resources (realistically it's to cover up old code with obfuscated and forgotten functionality.)

# Changelog (V1-V1.9)
Version 1.1 &mdash; Added update script

Version 1.2 &mdash; Added `<hr />` to end of long descriptions

Version 1.3 &mdash; Added documentation to the repository.

Version 1.4 &mdash; Added `<title>` and `<h1>` formatting support.

Version 1.5 &mdash; Updated the update script

Version 1.6 &mdash; Updated documentation and added template support

Version 1.7 &mdash; Changed bugs where links to other pdfs were being modified.

Version 1.8 &mdash; Images tags that were split to new files now render from the proper folder. Fixed issue where ROWCOLTABLE was not changing `</td>` to `</th>` for row headers.

Version 1.9 &mdash;
- Updated templates for solutions file.
- The environment `!ALTMARKERS!` can now be used to create images with the `static` class.
- The environment `!UNDERLINE!` can now be used to make underlines
- The argument `-a` can now be passed into handcrab's input file to appraise the TeX files for common canges.
- I have not updated documentation.
