cask 'dusty' do
  version '0.6.5'
  sha256 'd71115ca9029dcd82ba2394824d2da0a7a5a794eb07d2be936868f1f163383db'

  url "https://github.com/gamechanger/dusty/releases/download/#{version}/dusty.tar.gz"
  appcast 'https://github.com/gamechanger/dusty/releases.atom',
          :sha256 => 'c38f94f0be6d2b29a458994ca3f415c66557f4329de0b5926d66624264618b56'
  name 'Dusty'
  homepage 'https://github.com/gamechanger/dusty'
  license :mit

  depends_on :cask => 'dockertoolbox'
  container :type => :tar

  installer :script       => 'brew-install.sh',
            :must_succeed => true,
            :sudo         => true
  binary 'dusty'

  uninstall :launchctl => 'com.gamechanger.dusty'
end
