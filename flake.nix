{
  description = "TTS Storys";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/release-24.05";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
        };
        inherit (poetry2nix.lib.mkPoetry2Nix {inherit pkgs;}) mkPoetryApplication overrides defaultPoetryOverrides;
      in
        with pkgs; rec {
          # Development shell including selenium dependencies
          devShell = mkShell {
            name = "tts_stories";
            buildInputs = [
              pkgs.python310
              pkgs.poetry
            ];
            shellHook = ''
              poetry env use ${pkgs.lib.getExe pkgs.python310}
              export VIRTUAL_ENV=$(poetry env info --path)
              export PATH=$VIRTUAL_ENV/bin/:$PATH
              export LD_PRELOAD="$LD_PRELOAD:${pkgs.stdenv.cc.cc.lib}/lib/libstdc++.so.6"
            '';
          };

          # Runtime package with all dependencies using python version as default option.
          packages.app = mkPoetryApplication {
            projectDir = ./.;
            preferWheels = true;
            python = pkgs.python310;
            checkGroups = [];
          };

          defaultPackage = packages.app;
        }
    );
}
