cask 'dusty' do
  version '0.6.5'
  sha256 'd71115ca9029dcd82ba2394824d2da0a7a5a794eb07d2be936868f1f163383db'

  install_root = '/Library/LaunchDaemons'
  plist_name = 'com.gamechanger.dusty.plist'

  url "https://github.com/gamechanger/dusty/releases/download/#{version}/dusty.tar.gz"
  appcast 'https://github.com/gamechanger/dusty/releases.atom',
          :sha256 => 'c38f94f0be6d2b29a458994ca3f415c66557f4329de0b5926d66624264618b56'
  name 'Dusty'
  homepage 'https://github.com/gamechanger/dusty'
  license :mit

  depends_on :formula => 'git' if MacOS.release < :mavericks
  depends_on :cask => 'dockertoolbox'
  container :type => :tar

  installer :script => '/bin/cp',
            :args   => %W[#{staged_path}/#{plist_name} #{install_root}/#{plist_name}],
            :must_succeed => true,
            :sudo   => true
  installer :script       => '/bin/launchctl',
            :args         => %W[unload #{install_root}/#{plist_name}],
            :must_succeed => false,
            :sudo         => true
  installer :script       => "#{staged_path}/dusty",
            :args         => %w[-d --preflight-only],
            :must_succeed => true,
            :sudo         => true
  installer :script       => '/bin/launchctl',
            :args         => %W[load #{install_root}/#{plist_name}],
            :must_succeed => true,
            :sudo         => true
  binary 'dusty'

  uninstall :launchctl => plist_name
end
