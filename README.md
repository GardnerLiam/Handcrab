#	Handcrab &mdash; Handshrimp
## Version 0.1

## Changelog
- LaTeX preprocessing is now a thing we can do.
- Removed 4-comma and 4-semicolon environments
	- `!ROWTABLE!` is now required above `\begin{tabular}` and below `\end{tabular}` for row tables
	- `!ROWCOLTABLE!` is now required above `\begin{tabular}` and below `\end{tabular}` for row tables
	- `,,,,` is no longer required to surround images, but the `!ALTMARKER!`/`!ALTMARKERS!` have not changed.
- Added the `--keep-minipages` option to not remove minipages
- Added support for compiling multiple tex files into one
- Added skeleton files and format templates
- `!UNDERLINE!` no longer works ):
- More changes I can't immediately remember. 
