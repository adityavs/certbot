"""Tests for certbot_nginx.http_01"""
import unittest
import shutil

import mock
import six

from acme import challenges

from certbot import achallenges
from certbot import errors

from certbot.plugins import common_test
from certbot.tests import acme_util

from certbot_nginx import obj
from certbot_nginx.tests import util


class HttpPerformTest(util.NginxTest):
    """Test the NginxHttp01 challenge."""

    account_key = common_test.AUTH_KEY
    achalls = [
        achallenges.KeyAuthorizationAnnotatedChallenge(
            challb=acme_util.chall_to_challb(
                challenges.HTTP01(token=b"kNdwjwOeX0I_A8DXt9Msmg"), "pending"),
            domain="www.example.com", account_key=account_key),
        achallenges.KeyAuthorizationAnnotatedChallenge(
            challb=acme_util.chall_to_challb(
                challenges.HTTP01(
                    token=b"\xba\xa9\xda?<m\xaewmx\xea\xad\xadv\xf4\x02\xc9y"
                          b"\x80\xe2_X\t\xe7\xc7\xa4\t\xca\xf7&\x945"
                ), "pending"),
            domain="another.alias", account_key=account_key),
        achallenges.KeyAuthorizationAnnotatedChallenge(
            challb=acme_util.chall_to_challb(
                challenges.HTTP01(
                    token=b"\x8c\x8a\xbf_-f\\cw\xee\xd6\xf8/\xa5\xe3\xfd"
                          b"\xeb9\xf1\xf5\xb9\xefVM\xc9w\xa4u\x9c\xe1\x87\xb4"
                ), "pending"),
            domain="www.example.org", account_key=account_key),
        achallenges.KeyAuthorizationAnnotatedChallenge(
            challb=acme_util.chall_to_challb(
                challenges.HTTP01(token=b"kNdwjxOeX0I_A8DXt9Msmg"), "pending"),
            domain="sslon.com", account_key=account_key),
    ]

    def setUp(self):
        super(HttpPerformTest, self).setUp()

        config = util.get_nginx_configurator(
            self.config_path, self.config_dir, self.work_dir, self.logs_dir)

        from certbot_nginx import http_01
        self.sni = http_01.NginxHttp01(config)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.config_dir)
        shutil.rmtree(self.work_dir)

    def test_perform0(self):
        responses = self.sni.perform()
        self.assertEqual([], responses)

    @mock.patch("certbot_nginx.configurator.NginxConfigurator.save")
    def test_perform1(self, mock_save):
        self.sni.add_chall(self.achalls[0])
        response = self.achalls[0].response(self.account_key)

        responses = self.sni.perform()

        self.assertEqual([response], responses)
        self.assertEqual(mock_save.call_count, 1)

    def test_perform2(self):
        acme_responses = []
        for achall in self.achalls:
            self.sni.add_chall(achall)
            acme_responses.append(achall.response(self.account_key))

        sni_responses = self.sni.perform()

        self.assertEqual(len(sni_responses), 4)
        for i in six.moves.range(4):
            self.assertEqual(sni_responses[i], acme_responses[i])

    def test_mod_config(self):
        self.sni.add_chall(self.achalls[0])
        self.sni.add_chall(self.achalls[2])

        self.sni._mod_config()  # pylint: disable=protected-access

        self.sni.configurator.save()

        self.sni.configurator.parser.load()

        http = self.sni.configurator.parser.parsed[
            self.sni.configurator.parser.config_root][-1]

        vhosts = self.sni.configurator.parser.get_vhosts()

        for vhost in vhosts:
            pass
            # if the name matches
            # check that the location block is in there and is correct

            # if vhost.addrs == set(v_addr1):
            #     response = self.achalls[0].response(self.account_key)
            # else:
            #     response = self.achalls[2].response(self.account_key)
            #     self.assertEqual(vhost.addrs, set(v_addr2_print))
            # self.assertEqual(vhost.names, set([response.z_domain.decode('ascii')]))


if __name__ == "__main__":
    unittest.main()  # pragma: no cover