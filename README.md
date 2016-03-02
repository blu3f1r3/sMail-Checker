# sMail Account Checker

This simpleMail Account Checker will check if a account (format: &lt;email>:&lt;pass>) is valid by testing 
to login.


Options:
  -h, --help                          show this help message and exit
  -f FILE, --file FILE                File with <email>:<pass> each line
  -s SLEEP, --sleep SLEEP             Pause in seconds between each check
  -p PROVIDER, --provider PROVIDER    Specify a provider -p [tag] (e.g. gmail.com)
  -o filename, --output filename      Filename to write output into
  -n filename, --invalid filename     Filename to write invalid output into
  -i, --imap                          use IMAP first, then POP3 for unchecked. Some provider
                                      only offers IMAP.
  -l, --list                          List all supported provider tags
  -c, --colorize                      Add color to output
