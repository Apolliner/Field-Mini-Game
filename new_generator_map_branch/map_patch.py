def map_patch(name):
    """
        Содержит в себе и возвращает куски, вставлемые генератором в игровую карту
    """
    patch_dict = {
                  'river_3x3': [
                                '00bbb00',
                                '0bbbbb0',
                                'bbb~bbb',
                                'bb~~~bb',
                                'bbb~bbb',
                                '0bbbbb0',
                                '00bbb00',
                                ],
                  'river_4x4': [
                                '000bb000',
                                '00bbbb00',
                                '0bb~~bb0',
                                'bb~~~~bb',
                                'bb~~~~bb',
                                '0bb~~bb0',
                                '00bbbb00',
                                '000bb000',
                                ],
                  'river_5x5': [
                                '000bbb000',
                                '00bbbbb00',
                                '0bb~~~bb0',
                                'bb~~~~~bb',
                                'bb~~~~~bb',
                                'bb~~~~~bb',
                                '0bb~~~bb0',
                                '00bbbbb00',
                                '000bbb000',
                                ],
                  'river_6x6': [
                                '000bbbb000',
                                '00bbbbbb00',
                                '0bb~~~~bb0',
                                'bb~~~~~~bb',
                                'bb~~~~~~bb',
                                'bb~~~~~~bb',
                                'bb~~~~~~bb',
                                '0bb~~~~bb0',
                                '00bbbbbb00',
				'000bbbb000',
                                ],
                  'river_7x7': [
                                '0000bbb0000',
                                '000bbbbb000',
                                '00bb~~~bb00',
                                '0bb~~~~~bb0',
                                'bb~~~~~~~bb',
                                'bb~~~~~~~bb',
                                'bb~~~~~~~bb',
                                '0bb~~~~~bb0',
                                '00bb~~~bb00',
				'000bbbbb000',
				'0000bbb0000',
                                ],
                  'river_8x8': [
                                '0000bbbb0000',
                                '000bbbbbb000',
                                '00bb~~~~bb00',
                                '0bb~~~~~~bb0',
                                'bb~~~~~~~~bb',
                                'bb~~~~~~~~bb',
                                'bb~~~~~~~~bb',
                                'bb~~~~~~~~bb',
                                '0bb~~~~~~bb0',
				'00bb~~~~bb00',
				'000bbbbbb000',
				'0000bbbb0000',
                                ],
                  'river_9x9': [
                                '0000bbbbb0000',
                                '000bbbbbbb000',
                                '00bb~~~~~bb00',
                                '0bb~~~~~~~bb0',
                                'bb~~~~~~~~~bb',
                                'bb~~~~~~~~~bb',
                                'bb~~~~~~~~~bb',
                                'bb~~~~~~~~~bb',
                                'bb~~~~~~~~~bb',
				'0bb~~~~~~~bb0',
				'00bb~~~~~bb00',
				'000bbbbbbb000',
				'0000bbbbb0000',
                                ],
                  }

    if name in patch_dict:
        return patch_dict[name]
    else:
        return ['zzz', 'zzz', 'zzz',]

