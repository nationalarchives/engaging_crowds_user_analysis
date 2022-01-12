Getting Started

Make sure that pandas is available (e.g. within a virtualenv):
mkvirtualenv ec_engagement
pip install pandas

mkdir exports secrets
<Download classifications files to exports>
./pseudonymize.py

This will create all_classifications.csv at the top level
And secrets/identities.json

Common user ids across workflows and projects will be pseudonymised to the same
value within any given run. So long as the identities file is available from a
previous run, previously seen identities will continues to receive the same
pseudonym in the next run. So we are able to observe the behaviour of
(non-identifiable) individuals across all workflows and projects.

Where the user was not logged in, we have a hash of their IP address. Such users
receive a pseudonym beginning with prefix 'anon:'. These may or may not be the
same individual each time.

Where the user was logged in, they receive a pseudonym beginning 'name:'. These
are highly likely to be the same individual each time (modulo, say, shared accounts.)

The suffix part of the pseudonym is gloablly unique. In other words, there cannot be
both the pseudonyms 'anon:1' and 'name:1', as the '1' part will not be reused.