# MIT-licensed
class Skillctl < Formula
  include Language::Python::Virtualenv

  desc "Dependency resolver and bundle manager for Agent Skills"
  homepage "https://github.com/suthakamal2/skillctl"
  url "https://files.pythonhosted.org/packages/source/s/skillctl/skillctl-0.1.0.tar.gz"
  sha256 "REPLACE_ME_SHA256"
  license "MIT"

  depends_on "python@3.12"

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/source/P/PyYAML/PyYAML-6.0.tar.gz"
    sha256 "REPLACE_ME_PYYAML_SHA256"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.7.0.tar.gz"
    sha256 "REPLACE_ME_RICH_SHA256"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "0.1.0", shell_output("#{bin}/skillctl --version")
  end
end
