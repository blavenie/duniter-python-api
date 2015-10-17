#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
# Caner Candan <caner@candan.fr>, http://caner.candan.fr
#

from .. import History, logging

logger = logging.getLogger("ucoin/tx")


class Blocks(History):
    """

    """
    def __init__(self, conn_handler, pubkey, from_, to_, module='tx'):
        """

        """
        super(Blocks, self).__init__(conn_handler, pubkey, module)
        self.from_ = from_
        self.to_ = to_

    def __get__(self, **kwargs):
        """

        """
        r = yield from self.requests_get('/history/%s/blocks/%s/%s' % (self.pubkey, self.from_, self.to_), **kwargs)
        return (yield from r.json())
