#! /bin/bash

set -e
set -x

git ls-files | xargs zip service.zip
scp service.zip sinclair@sinclairtarget.com:/var/www/sinclairtarget.com/baked
