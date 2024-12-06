{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  # https://devenv.sh/basics/
  dotenv.enable = true;
  # dotenv.filename = ".env";

  # https://devenv.sh/packages/
  packages = [pkgs.git pkgs.espeak];

  # https://devenv.sh/languages/
  languages.python.enable = true;
  languages.python.package = pkgs.python310;
  languages.python.uv.enable = true;

  enterShell = ''
    # Workaround for language.python.library not working with uv
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib/";
    source $UV_PROJECT_ENVIRONMENT/bin/activate
  '';

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
    uv run pytest .
  '';

  # https://devenv.sh/pre-commit-hooks/
  pre-commit.hooks.shellcheck.enable = true;
  pre-commit.hooks.ruff.enable = true;
  pre-commit.hooks.ruff-format.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
