pip install notebook
pip install nbdev
nbdev_install_quarto
pip install jupyter_contrib_nbextensions
jupyter contrib nbextension install --user
jupyter nbextension enable collapsible_headings/main
jupyter nbextension enable toc2/main
pip install jupyter_nbextensions_configurator
nbdev_install_hooks
nbdev-extensions