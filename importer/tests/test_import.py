from unittest import mock


def test_importer():
    with mock.patch('importer.management.commands._reddit.do_import') as reddit_import:
        with mock.patch('importer.management.commands._rss.do_import') as rss_import:
            with mock.patch('importer.management.commands._cleanup.do_cleanup') as cleanup:
                with mock.patch('importer.management.commands.importer.logger') as logger:
                    from importer.management.commands.importer import Command

                    cmd = Command()
                    cmd.handle()
                    reddit_import.assert_called_once()
                    rss_import.assert_called_once()
                    cleanup.assert_called_once()

                    reddit_import.reset_mock()
                    rss_import.reset_mock()
                    cleanup.reset_mock()

                    reddit_import.side_effect = Exception("reddit error")
                    rss_import.side_effect = Exception("rss error")
                    cleanup.side_effect = Exception("cleanup error")
                    cmd = Command()
                    cmd.handle()

                    logger.error.assert_has_calls([
                        mock.call('Error when trying to do reddit import : reddit error'),
                        mock.call('Error when trying to do rss import : rss error'),
                        mock.call('Error when doing clean up : cleanup error'),
                    ])
