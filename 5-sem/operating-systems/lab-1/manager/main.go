package main

import (
	"bufio"
	"fmt"
	"lab-1/manager/controller"
	"os"
	"strconv"
	"strings"
)

func main() {
	manager := &controller.ManagerController{}

	// Initialize connections with appropriate addresses.
	if err := manager.InitConnections("localhost:8001", "localhost:8002"); err != nil {
		fmt.Println("Error initializing connections:", err)
		os.Exit(1)
	}

	// Start the manager.
	if err := manager.StartManager(); err != nil {
		fmt.Println("Error starting manager:", err)
		os.Exit(1)
	}

	reader := bufio.NewReader(os.Stdin)

	for {
		printMenu()
		option, err := readOption(reader)
		if err != nil {
			fmt.Println("Invalid option. Please try again.")
			continue
		}

		switch option {
		case 1:
			// Start computations
			arg := readInt("Enter the argument for computations: ")
			if err := manager.StartComputations(int64(arg)); err != nil {
				fmt.Println("Error starting computations:", err)
			}
		case 2:
			// Get computation statuses
			if err := manager.GetComputationStatuses(); err != nil {
				fmt.Println("Error getting computation statuses:", err)
			}
		case 3:
			// Cancel computations
			if err := manager.CancelComputations(); err != nil {
				fmt.Println("Error canceling computations:", err)
			}
		case 4:
			// Exit the program
			os.Exit(0)
		default:
			fmt.Println("Invalid option. Please try again.")
		}
	}
}

func printMenu() {
	fmt.Println("Console GUI Menu")
	fmt.Println("1. Start Computations")
	fmt.Println("2. Get Computation Statuses")
	fmt.Println("3. Cancel Computations")
	fmt.Println("4. Exit")
	fmt.Print("Select an option: ")
}

func readOption(reader *bufio.Reader) (int, error) {
	input, _ := reader.ReadString('\n')
	option, err := strconv.Atoi(strings.TrimSpace(input))
	if err != nil {
		return 0, err
	}
	return option, nil
}

func readInt(prompt string) int {
	reader := bufio.NewReader(os.Stdin)
	for {
		fmt.Print(prompt)
		input, _ := reader.ReadString('\n')
		arg, err := strconv.Atoi(strings.TrimSpace(input))
		if err == nil {
			return arg
		}
		fmt.Println("Invalid input. Please enter a valid integer.")
	}
}
