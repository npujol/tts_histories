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

  # https://devenv.sh/processes/
  # processes.cargo-watch.exec = "cargo-watch";

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/scripts/
  # scripts.hello.exec = ''
  #   echo hello from $GREET
  # '';

  env.LD_PRELOAD = "${pkgs.stdenv.cc.cc.lib}/lib/libstdc++.so.6";
  # enterShell = ''
  #   export LD_PRELOAD="$LD_PRELOAD:${pkgs.stdenv.cc.cc.lib}/lib/libstdc++.so.6"
  # '';

  # https://devenv.sh/tasks/
  # tasks = {
  #   "myproj:setup".exec = "mytool build";
  #   "devenv:enterShell".after = [ "myproj:setup" ];
  # };

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
