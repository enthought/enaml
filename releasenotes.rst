Enaml Release Notes
===================

0.6.3 - 12/11/2012
------------------
- Fix critical bug related to traits Disallow and the `attr` keyword. 25755e2bbd_

0.6.2 - 12/11/2012
------------------
- Fix critical bug for broken dynamic scoping. a788869ab0_

0.6.1 - 12/10/2012
------------------
- Fix critical bug in compiler and expression objects. dfb6f648a1_

0.6.0 - 12/10/2012
------------------
- Add Icon and Image support using a lazy loading resource sub-framework. 77d5ca3b01_
- Add a traitsui support via the TraitsItem widget (care of Steven Silvester). 9cb9126da1_
- Add matplotlib support via the MPLCanvas widget (care of Steven Silvester). eaa6294566_
- Updated Session api which is more intuitive and easier to use.
- Updated Object api which is more intuitive and easier to use.
- Object lifecycle reflected in a `state` attribute.
- Huge reduction in memory usage when creating large numbers of objects.
- Huge reduction in time to create large numbers of objects.
- New widget registry make it easier to register custom widgets. cc791a52d7_
- Better and faster code analysis via code tracers. 4eceb09f70_
- Fix a parser bug related to relative imports. 3e43e73e90_
- Various other tweaks, bugfixes, and api cleanup.

0.5.1 - 11/19/2012
------------------
- Fix a method naming bug in QSingleWidgetLayout. 7a4c9de7e6_
- Fix a test height computation bug in QFlowLayout. a962d2ae78_
- Invalidate the QFlowLayout on layout request. 1e91a54245_
- Dispatch child events immediately when possible. e869f7124f_
- Destroy child widgets after the children change event is emitted. c695ae35ee_
- Add a preliminary WebView widget. 27faa381dc_

0.5.0 - 11/16/2012
------------------
- Merge the feature-async branch into mainline. f86dad8f6e_
- First release with release notes. 8dbed4b9cd_

.. _25755e2bbd: https://github.com/enthought/enaml/commit/25755e2bbd5e2e38e42d30776e1864d52c992af3
.. _a788869ab0: https://github.com/enthought/enaml/commit/a788869ab0a410c478cbe4cc066fc8ee35b266b8
.. _dfb6f648a1: https://github.com/enthought/enaml/commit/dfb6f648a15370249b0a57433b8839a4caba7d35
.. _77d5ca3b01: https://github.com/enthought/enaml/commit/77d5ca3b0135fa982663d4ce9cf801119617c611
.. _eaa6294566: https://github.com/enthought/enaml/commit/eaa62945663fa9c96aee822c9f31ef966c88fd62
.. _9cb9126da1: https://github.com/enthought/enaml/commit/9cb9126da1e590814ad6dbee9a732c9add185ed6
.. _cc791a52d7: https://github.com/enthought/enaml/commit/cc791a52d772b07c7482427b5b60dcff9d5436c1
.. _4eceb09f70: https://github.com/enthought/enaml/commit/4eceb09f707e7795182013b9f874abf0afbaab41
.. _3e43e73e90: https://github.com/enthought/enaml/commit/3e43e73e90bd392a63a1faa53f821672fdb8c44f
.. _27faa381dc: https://github.com/enthought/enaml/commit/27faa381dc5dd6c5cc41a0826df35b71339d3e7e
.. _c695ae35ee: https://github.com/enthought/enaml/commit/c695ae35ee9fcf35964df88831de0d3b30883f78
.. _e869f7124f: https://github.com/enthought/enaml/commit/e869f7124f0e13bea7f35d5f5a91bc89dc1dcd4e
.. _1e91a54245: https://github.com/enthought/enaml/commit/1e91a542452662ebd3dfe9d5a854ec2277f4415d
.. _a962d2ae78: https://github.com/enthought/enaml/commit/a962d2ae78488398cbe50d4ad16bd1cd90a1060b
.. _7a4c9de7e6: https://github.com/enthought/enaml/commit/7a4c9de7e6342b65efd6e3e841be0adfad286d99
.. _8dbed4b9cd: https://github.com/enthought/enaml/commit/8dbed4b9cd16d8c9f71ea63dfd92494176fdf753
.. _f86dad8f6e: https://github.com/enthought/enaml/commit/f86dad8f6e3fe0bf07a2cf59765aaa3b934fa233