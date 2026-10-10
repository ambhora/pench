# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""Version metadata for pench."""

import semver as SemVer

__version__ = "0.0.1"

# semver 3 renamed VersionInfo to Version and deprecated the old name.
_parser = getattr(SemVer, "Version", None) or SemVer.VersionInfo
semver = _parser.parse(__version__)
