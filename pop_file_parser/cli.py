"""
Интерфейс командной строки для работы с компилятором.
"""
import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .compiler import PopFileCompiler

console = Console()

@click.group()
def cli():
    """TF2 MvM .pop file compiler and editor."""
    pass

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def info(file_path):
    """Показать информацию о pop файле."""
    compiler = PopFileCompiler()
    
    try:
        compiler.load_file(file_path)
        
        # Создаем таблицу с информацией о миссии
        table = Table(title=f"Mission: {compiler.mission_name}")
        
        table.add_column("Wave ID", justify="right", style="cyan")
        table.add_column("Robots", justify="right", style="green")
        table.add_column("Currency", justify="right", style="yellow")
        table.add_column("Support", style="magenta")
        
        for wave in compiler.waves:
            table.add_row(
                str(wave.id),
                str(len(wave.robots)),
                str(wave.totalcurrency or 'N/A'),
                "Limited" if wave.support_limited else "Unlimited"
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def validate(file_path):
    """Проверить валидность pop файла."""
    compiler = PopFileCompiler()
    
    try:
        compiler.load_file(file_path)
        if compiler.validate():
            console.print("[green]File is valid![/green]")
        else:
            console.print("[red]File contains errors![/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--wave-id', type=int, required=True, help='ID волны для редактирования')
@click.option('--robot-count', type=int, help='Новое количество роботов')
@click.option('--currency', type=int, help='Новое количество валюты')
@click.option('--support', type=click.Choice(['limited', 'unlimited']), 
              help='Тип поддержки')
def edit_wave(file_path, wave_id, robot_count, currency, support):
    """Редактировать параметры волны."""
    compiler = PopFileCompiler()
    
    try:
        compiler.load_file(file_path)
        
        params = {}
        if robot_count is not None:
            params['totalcount'] = robot_count
        if currency is not None:
            params['totalcurrency'] = currency
        if support is not None:
            params['support_limited'] = support == 'limited'
            
        compiler.modify_wave(wave_id, params)
        
        # Создаем резервную копию
        path = Path(file_path)
        backup_path = path.with_suffix('.pop.bak')
        path.rename(backup_path)
        
        # Сохраняем изменения
        compiler.export(file_path)
        console.print("[green]Changes saved successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('file_path', type=click.Path())
def create(file_path):
    """Создать новый pop файл."""
    if Path(file_path).exists():
        console.print("[red]Error: File already exists![/red]")
        sys.exit(1)
        
    compiler = PopFileCompiler()
    compiler.mission_name = "New Mission"
    
    # Добавляем пример волны
    compiler.waves.append({
        "id": 1,
        "description": "First Wave",
        "totalcount": 10,
        "totalcurrency": 100,
        "robots": []
    })
    
    try:
        compiler.export(file_path)
        console.print("[green]New mission created successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
def export(input_path, output_path):
    """Экспортировать pop файл."""
    compiler = PopFileCompiler()
    
    try:
        compiler.load_file(input_path)
        compiler.export(output_path)
        console.print("[green]File exported successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

def main():
    """Точка входа для CLI."""
    cli()
